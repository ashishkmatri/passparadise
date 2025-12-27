#!/bin/bash
# =============================================================
# BACKUP (AMI) and DESTROY Instance
# Cost: Only pay for AMI snapshot (~$0.05/GB/month = ~$1.50/month for 30GB)
# Savings: ~95% vs running, ~60% vs stopped
# Use when: Not using for weeks/months
# =============================================================

set -e

echo "📸 Creating Backup and Destroying Instance..."
echo ""

# Get instance ID
INSTANCE_ID=$(terraform output -raw instance_id 2>/dev/null)

if [ -z "$INSTANCE_ID" ]; then
    echo "❌ No instance found."
    exit 1
fi

# Check if instance is stopped
STATE=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region ap-south-1 \
    --query 'Reservations[0].Instances[0].State.Name' \
    --output text)

if [ "$STATE" != "stopped" ]; then
    echo "⏳ Stopping instance first..."
    aws ec2 stop-instances --instance-ids "$INSTANCE_ID" --region ap-south-1
    aws ec2 wait instance-stopped --instance-ids "$INSTANCE_ID" --region ap-south-1
fi

# Create AMI backup
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
AMI_NAME="youtube-automation-backup-$TIMESTAMP"

echo "📸 Creating AMI backup: $AMI_NAME"

AMI_ID=$(aws ec2 create-image \
    --instance-id "$INSTANCE_ID" \
    --name "$AMI_NAME" \
    --description "YouTube Automation backup - $TIMESTAMP" \
    --region ap-south-1 \
    --output text)

echo "⏳ Waiting for AMI to be available..."
aws ec2 wait image-available --image-ids "$AMI_ID" --region ap-south-1

# Save AMI ID for restore
echo "$AMI_ID" > .last_backup_ami
echo "$TIMESTAMP" > .last_backup_time

echo ""
echo "=============================================="
echo "✅ Backup Created!"
echo "=============================================="
echo "AMI ID:   $AMI_ID"
echo "AMI Name: $AMI_NAME"
echo ""

# Confirm destruction
read -p "🗑️  Destroy instance now? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled. Instance still exists."
    exit 0
fi

# Destroy with Terraform
echo "🗑️  Destroying infrastructure..."
terraform destroy -auto-approve

echo ""
echo "=============================================="
echo "✅ Destruction Complete!"
echo "=============================================="
echo ""
echo "💾 Backup saved as: $AMI_ID"
echo "   Stored in: .last_backup_ami"
echo ""
echo "💰 Cost Now:"
echo "   ✓ EC2:     ₹0"
echo "   ✓ EBS:     ₹0"
echo "   ✓ AMI:     ~₹125/month (30GB snapshot)"
echo "   ✓ Total:   ~₹125/month"
echo ""
echo "📋 To Restore Later:"
echo "   ./restore.sh"
echo "=============================================="
