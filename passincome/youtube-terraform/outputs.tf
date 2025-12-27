# =============================================================
# Outputs for YouTube Automation EC2 (Spot + Persistent Data Volume)
# =============================================================

output "spot_request_id" {
  description = "Spot Instance Request ID"
  value       = aws_spot_instance_request.youtube_server.id
}

output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_spot_instance_request.youtube_server.spot_instance_id
}

output "public_ip" {
  description = "Public IP address"
  value       = aws_spot_instance_request.youtube_server.public_ip
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ~/.ssh/youtube-ec2-key ubuntu@${aws_spot_instance_request.youtube_server.public_ip}"
}

output "data_volume_id" {
  description = "Persistent data volume ID (survives spot interruptions)"
  value       = aws_ebs_volume.youtube_data.id
}

output "data_volume_az" {
  description = "Data volume availability zone"
  value       = aws_ebs_volume.youtube_data.availability_zone
}

output "monthly_cost_estimate" {
  description = "Estimated monthly cost"
  value       = "Spot: ~$8-12 | Data volume (30GB): ~$2.40 | Snapshots: ~$2-3 | Total: ~$12-18/month"
}
