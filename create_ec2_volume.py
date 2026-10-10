
import boto3
from pathlib import Path
from botocore.exceptions import ClientError

# 1. Select your AWS Region
REGION = "ap-south-1"

# 2. Resource names and volume size
KEY_NAME = "ubuntu-key"
INSTANCE_NAME = "demo-ec2"
VOLUME_NAME = "demo-volume"
VOLUME_SIZE = 8   #GIB

ec2 = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)


def main():
    try:
        # STEP 1: Find the latest Ubuntu Server 24.04 LTS AMI
        images = ec2.describe_images(
            Owners=["099720109477"],  # Canonical (Ubuntu)
            Filters=[
                {
                    "Name": "name",
                    "Values": [
                        "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"
                    ],
                },
                {"Name": "state", "Values": ["available"]},
                {"Name": "architecture", "Values": ["x86_64"]},
                {"Name": "root-device-type", "Values": ["ebs"]},
            ],
        )["Images"]

        if not images:
            raise RuntimeError(
                "No matching Ubuntu AMI found in this Region."
            )

        latest_image = max(
            images, key=lambda image: image["CreationDate"]
        )
        ami_id = latest_image["ImageId"]

        print("Ubuntu AMI:", ami_id)
        print("Ubuntu image:", latest_image["Name"])

        # STEP 2: Create a key pair and save the private key
        key_path = Path.cwd() / f"{KEY_NAME}.pem"

        try:
            key = ec2.create_key_pair(KeyName=KEY_NAME)
            key_path.write_text(key["KeyMaterial"], encoding="utf-8")

            # Restrict access to the private key on Windows
            import os
            if os.name == "nt":
                os.chmod(key_path, 0o600)

            print("Private key saved to:", key_path)
        except ClientError as error:
            if error.response["Error"]["Code"] == "InvalidKeyPair.Duplicate":
                raise RuntimeError(
                    f"Key pair '{KEY_NAME}' already exists. "
                    "Use a new name or safely recover your existing key."
                )
            raise

        # STEP 3: Launch the EC2 instance
        response = ec2.run_instances(
            ImageId=ami_id,
            InstanceType="t3.micro",
            KeyName=KEY_NAME,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": INSTANCE_NAME}
                    ],
                }
            ],
        )

        instance_id = response["Instances"][0]["InstanceId"]
        instance = ec2_resource.Instance(instance_id)

        print("EC2 instance created:", instance_id)
        print("Waiting for instance to run...")

        instance.wait_until_running()
        instance.reload()

        # STEP 4: Create an EBS volume in the SAME Availability Zone
        availability_zone = instance.placement["AvailabilityZone"]

        volume_response = ec2.create_volume(
            AvailabilityZone=availability_zone,
            Size=VOLUME_SIZE,
            VolumeType="gp3",
            TagSpecifications=[
                {
                    "ResourceType": "volume",
                    "Tags": [
                        {"Key": "Name", "Value": VOLUME_NAME}
                    ],
                }
            ],
        )

        
        volume_id = volume_response["VolumeId"]
        volume = ec2_resource.Volume(volume_id)

        print("EBS volume created:", volume_id)
        print("Waiting for volume to become available...")

        ec2.get_waiter("volume_available").wait(
            VolumeIds=[volume_id],
            WaiterConfig={
                "Delay": 5,
                "MaxAttempts": 60
            }
        )

        print("EBS volume is available.")

        # STEP 5: Attach the volume to the instance
        ec2.attach_volume(
            VolumeId=volume_id,
            InstanceId=instance_id,
            Device="/dev/sdf",
        )


        print("Waiting for volume attachment...")
        waiter = ec2.get_waiter("volume_in_use")
        waiter.wait(VolumeIds=[volume_id])

        print("\nSUCCESS!")
        print("Instance ID:", instance_id)
        print("Instance type: t3.micro")
        print("AMI ID:", ami_id)
        print("Availability Zone:", availability_zone)
        print("Volume ID:", volume_id)
        print("Volume size:", VOLUME_SIZE, "GiB")
        print("Key file:", key_path)
        print("Volume attached to EC2.")

    except (ClientError, RuntimeError) as error:
        print("AWS operation failed:", error)


if __name__ == "__main__":
    main()