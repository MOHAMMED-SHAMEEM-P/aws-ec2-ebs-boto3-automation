# AWS Infrastructure Automation Using Python and Boto3

## Project Overview

This project demonstrates the automated provisioning of AWS compute and storage resources using Python and Boto3.

The script discovers an Ubuntu Server 24.04 LTS Amazon Machine Image (AMI), creates an EC2 key pair, launches a `t3.micro` instance, provisions an 8 GiB gp3 EBS volume, and attaches the volume to the instance.

## Technologies Used

- Python
- Boto3 (AWS SDK for Python)
- Amazon EC2
- Amazon EBS
- Ubuntu Server 24.04 LTS
- AWS CLI

## Automated Workflow

1. Discover an available Ubuntu AMI in the selected AWS Region.
2. Create an EC2 key pair and save its private key locally.
3. Launch an EC2 instance.
4. Identify the instance's Availability Zone.
5. Create an 8 GiB gp3 EBS volume in the same Availability Zone.
6. Wait for the volume to become available.
7. Attach the volume to the EC2 instance and wait for attachment.

## Prerequisites

- Python installed
- Boto3 installed using `python -m pip install boto3`
- AWS CLI configured with appropriate AWS credentials and permissions
- A usable VPC and subnet in the selected Region

## Configuration

- AWS Region: `ap-south-1`
- Operating System: Ubuntu Server 24.04 LTS
- Instance Type: `t3.micro`
- EBS Volume: 8 GiB, `gp3`

## Run the Project

```bash
python create_ec2_volume.py
```

## Security Considerations

- Do not commit private key files or AWS credentials.
- Use least-privilege IAM permissions.
- Restrict SSH access to trusted IP addresses if remote access is configured.
- Verify AWS pricing and clean up resources after testing.

## Learning Outcomes

This project provided practical experience with AWS API operations, Python-based infrastructure automation, EC2 provisioning, EBS volume management, and AWS resource waiters.

## Project Status

Learning project. Verify resource creation and attachment in the AWS Console before describing a run as successful.
