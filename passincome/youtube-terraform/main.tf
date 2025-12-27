# =============================================================
# YouTube Automation EC2 - Main Terraform Configuration
# =============================================================
# Cost-saving strategy:
# - Start/Stop: Pay only compute when working
# - Backup/Destroy: Pay nothing when not using for days/weeks
# =============================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "youtube-automation"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

# =============================================================
# DATA SOURCES
# =============================================================

# Get latest Ubuntu 22.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Get current IP for SSH access
data "http" "my_ip" {
  url = "https://ipv4.icanhazip.com"
}

# =============================================================
# SECURITY GROUP
# =============================================================

resource "aws_security_group" "youtube_sg" {
  name        = "youtube-automation-sg"
  description = "Security group for YouTube automation server"

  # SSH access
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  # Outbound internet access
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "youtube-automation-sg"
  }
}

# =============================================================
# SSH KEY PAIR
# =============================================================

resource "aws_key_pair" "youtube_key" {
  key_name   = "youtube-automation-key"
  public_key = var.ssh_public_key

  tags = {
    Name = "youtube-automation-key"
  }
}

# =============================================================
# PERSISTENT DATA VOLUME (survives spot interruptions)
# =============================================================

# Get availability zone for the data volume
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  az = data.aws_availability_zones.available.names[0]
}

resource "aws_ebs_volume" "youtube_data" {
  availability_zone = local.az
  size              = var.data_volume_size
  type              = "gp3"

  tags = {
    Name = "youtube-automation-data"
  }

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = false  # Set to true after initial setup to prevent accidents
  }
}

# =============================================================
# EC2 SPOT INSTANCE (60-90% cheaper than on-demand)
# =============================================================

resource "aws_spot_instance_request" "youtube_server" {
  ami           = var.restore_from_ami != "" ? var.restore_from_ami : data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  # Spot configuration
  spot_type            = "one-time"
  wait_for_fulfillment = true

  # Must be in same AZ as data volume
  availability_zone = local.az

  key_name                    = aws_key_pair.youtube_key.key_name
  vpc_security_group_ids      = [aws_security_group.youtube_sg.id]
  associate_public_ip_address = true

  # Small root volume for OS only (data goes on separate volume)
  root_block_device {
    volume_size           = 10
    volume_type           = "gp3"
    delete_on_termination = true  # OK to delete, data is on separate volume
  }

  # User data: setup + mount data volume
  user_data = <<-EOF
              #!/bin/bash
              set -e

              # Wait for data volume to be attached
              while [ ! -e /dev/xvdf ]; do sleep 1; done

              # Format if new volume (check if has filesystem)
              if ! blkid /dev/xvdf; then
                mkfs.ext4 /dev/xvdf
              fi

              # Mount data volume
              mkdir -p /data
              mount /dev/xvdf /data

              # Add to fstab for auto-mount on reboot
              echo '/dev/xvdf /data ext4 defaults,nofail 0 2' >> /etc/fstab

              # Create project directory on data volume
              mkdir -p /data/youtube-automation
              ln -sf /data/youtube-automation /home/ubuntu/youtube-automation
              chown -R ubuntu:ubuntu /data/youtube-automation

              # Update system
              apt-get update
              apt-get upgrade -y

              # Install dependencies
              apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                ffmpeg \
                git \
                espeak-ng \
                htop

              # Install Python packages globally
              pip3 install --break-system-packages \
                edge-tts \
                Pillow \
                numpy \
                pydub \
                requests

              # Mark setup complete
              touch /home/ubuntu/.setup_complete
              echo "Setup complete!" >> /var/log/user-data.log
              EOF

  tags = {
    Name = "youtube-automation-server"
  }
}

# Attach data volume to spot instance
resource "aws_volume_attachment" "youtube_data_attach" {
  device_name = "/dev/xvdf"
  volume_id   = aws_ebs_volume.youtube_data.id
  instance_id = aws_spot_instance_request.youtube_server.spot_instance_id

  # Don't force detach - let instance shutdown gracefully
  force_detach = false
}

# Tag the spot instance after creation
resource "aws_ec2_tag" "youtube_server_name" {
  resource_id = aws_spot_instance_request.youtube_server.spot_instance_id
  key         = "Name"
  value       = "youtube-automation-server"
}

# =============================================================
# AUTOMATED EBS SNAPSHOTS (Data Lifecycle Manager)
# =============================================================

# IAM role for DLM
resource "aws_iam_role" "dlm_lifecycle_role" {
  name = "youtube-dlm-lifecycle-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "dlm.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "dlm_lifecycle_policy" {
  name = "youtube-dlm-lifecycle-policy"
  role = aws_iam_role.dlm_lifecycle_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateSnapshot",
          "ec2:CreateSnapshots",
          "ec2:DeleteSnapshot",
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "ec2:DescribeSnapshots"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["ec2:CreateTags"]
        Resource = "arn:aws:ec2:*::snapshot/*"
      }
    ]
  })
}

# DLM policy - disabled due to IAM permissions issue
# TODO: Fix IAM permissions for DLM and re-enable
# resource "aws_dlm_lifecycle_policy" "youtube_backup" {
#   description        = "YouTube automation hourly backup"
#   execution_role_arn = aws_iam_role.dlm_lifecycle_role.arn
#   state              = "ENABLED"
#
#   policy_details {
#     resource_types = ["VOLUME"]
#
#     schedule {
#       name = "Hourly snapshots"
#
#       create_rule {
#         interval      = 1
#         interval_unit = "HOURS"
#         times         = ["00:00"]  # Start at midnight UTC
#       }
#
#       retain_rule {
#         count = 24  # Keep last 24 hourly snapshots
#       }
#
#       tags_to_add = {
#         SnapshotCreator = "DLM"
#         Project         = "youtube-automation"
#       }
#
#       copy_tags = true
#     }
#
#     target_tags = {
#       Name = "youtube-automation-data"
#     }
#   }
#
#   tags = {
#     Name = "youtube-automation-dlm"
#   }
# }

# =============================================================
# ELASTIC IP (Optional - costs money but keeps same IP)
# =============================================================

# Uncomment if you want persistent IP (costs ~$3.5/month when instance stopped)
# resource "aws_eip" "youtube_ip" {
#   instance = aws_spot_instance_request.youtube_server.spot_instance_id
#   domain   = "vpc"
#
#   tags = {
#     Name = "youtube-automation-ip"
#   }
# }
