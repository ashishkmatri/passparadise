#!/bin/bash
# =============================================================
# RESTORE from AMI Backup
# Creates new instance from last backup
# All your data, scripts, and settings preserved!
# =============================================================

set -e

echo "🔄 Restoring YouTube Automation Server from Backup..."
echo ""

# Check for backup AMI
if [ -f ".last_backup_ami" ]; then
    AMI_ID=$(cat .last_backup_ami)
    BACKUP_TIME=$(cat .last_backup_time 2>/dev/null || echo "unknown")
    echo "📦 Found backup:"
    echo "   AMI ID: $AMI_ID"
    echo "   Created: $BACKUP_TIME"
    echo ""
else
    echo "❌ No backup found. Looking for available AMIs..."
    echo ""
    
    # List available backups
    aws ec2 describe-images \
        --owners self \
        --region ap-south-1 \
        --filters "Name=name,Values=youtube-automation-backup-*" \
        --query 'Images[*].[ImageId,Name,CreationDate]' \
        --output table
    
    echo ""
    read -p "Enter AMI ID to restore: " AMI_ID
fi

# Verify AMI exists
AMI_STATE=$(aws ec2 describe-images \
    --image-ids "$AMI_ID" \
    --region ap-south-1 \
    --query 'Images[0].State' \
    --output text 2>/dev/null || echo "not-found")

if [ "$AMI_STATE" != "available" ]; then
    echo "❌ AMI $AMI_ID not found or not available."
    exit 1
fi

echo "✅ AMI verified: $AMI_ID"
echo ""

# Update terraform.tfvars with restore AMI
if [ -f "terraform.tfvars" ]; then
    # Update existing tfvars
    if grep -q "restore_from_ami" terraform.tfvars; then
        sed -i "s|restore_from_ami.*|restore_from_ami = \"$AMI_ID\"|" terraform.tfvars
    else
        echo "restore_from_ami = \"$AMI_ID\"" >> terraform.tfvars
    fi
else
    echo "❌ terraform.tfvars not found. Please create it first."
    exit 1
fi

echo "🚀 Restoring infrastructure..."
terraform apply -auto-approve

# Get new instance details
INSTANCE_ID=$(terraform output -raw instance_id)
PUBLIC_IP=$(terraform output -raw public_ip)

# Clear restore_from_ami for next fresh install
sed -i 's|restore_from_ami.*|restore_from_ami = ""|' terraform.tfvars

echo ""
echo "=============================================="
echo "✅ Restore Complete!"
echo "=============================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP:   $PUBLIC_IP"
echo ""
echo "SSH Command:"
echo "ssh -i ~/.ssh/youtube-key ubuntu@$PUBLIC_IP"
echo ""
echo "📋 Your data and scripts are restored!"
echo ""
echo "💡 Tip: You can delete old AMI to save ~₹125/month:"
echo "   aws ec2 deregister-image --image-id $AMI_ID --region ap-south-1"
echo "=============================================="
