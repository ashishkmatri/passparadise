# =============================================================
# Variables for YouTube Automation EC2
# =============================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"  # Mumbai
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"  # 4GB RAM, 2 vCPU
}

variable "storage_size" {
  description = "Root volume size in GB (OS only)"
  type        = number
  default     = 10
}

variable "data_volume_size" {
  description = "Data volume size in GB (persists across spot interruptions)"
  type        = number
  default     = 30
}

variable "ssh_public_key" {
  description = "SSH public key for EC2 access"
  type        = string
}

variable "restore_from_ami" {
  description = "AMI ID to restore from (leave empty for fresh install)"
  type        = string
  default     = ""
}
