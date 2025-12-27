#!/bin/bash
# =============================================================
# STATUS - Check current state and costs
# =============================================================

echo ""
echo "=============================================="
echo "📊 YouTube Automation - Status"
echo "=============================================="
echo ""

# Check if Terraform state exists
if [ ! -f "terraform.tfstate" ]; then
    echo "Status: ❌ Not Deployed"
    echo ""
    echo "To create: terraform apply"
    
    # Check for backups
    if [ -f ".last_backup_ami" ]; then
        echo ""
        echo "📦 Backup Available:"
        echo "   AMI: $(cat .last_backup_ami)"
        echo "   To restore: ./restore.sh"
    fi
    exit 0
fi

# Get instance info
INSTANCE_ID=$(terraform output -raw instance_id 2>/dev/null || echo "")

if [ -z "$INSTANCE_ID" ]; then
    echo "Status: ❌ No instance in state"
    exit 0
fi

# Get instance state
STATE=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region ap-south-1 \
    --query 'Reservations[0].Instances[0].State.Name' \
    --output text 2>/dev/null || echo "not-found")

PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region ap-south-1 \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text 2>/dev/null || echo "N/A")

echo "Instance ID: $INSTANCE_ID"
echo ""

case $STATE in
    "running")
        echo "Status: 🟢 RUNNING"
        echo "Public IP: $PUBLIC_IP"
        echo ""
        echo "💰 Current Cost: ~₹100/day (~₹3000/month)"
        echo ""
        echo "SSH: ssh -i ~/.ssh/youtube-key ubuntu@$PUBLIC_IP"
        echo ""
        echo "Actions:"
        echo "  ./stop.sh              - Stop (save ~90%)"
        echo "  ./backup-and-destroy.sh - Backup & destroy (save ~95%)"
        ;;
    "stopped")
        echo "Status: 🟡 STOPPED"
        echo ""
        echo "💰 Current Cost: ~₹7/day (~₹200/month) - Storage only"
        echo ""
        echo "Actions:"
        echo "  ./start.sh             - Start working"
        echo "  ./backup-and-destroy.sh - Backup & destroy (save more)"
        ;;
    "not-found")
        echo "Status: ❌ Instance not found (destroyed?)"
        echo ""
        if [ -f ".last_backup_ami" ]; then
            echo "📦 Backup Available: $(cat .last_backup_ami)"
            echo "   To restore: ./restore.sh"
        fi
        ;;
    *)
        echo "Status: ⚪ $STATE"
        ;;
esac

echo ""
echo "=============================================="

# Show available backups
echo ""
echo "📦 Available Backups:"
aws ec2 describe-images \
    --owners self \
    --region ap-south-1 \
    --filters "Name=name,Values=youtube-automation-backup-*" \
    --query 'Images[*].[ImageId,Name,CreationDate]' \
    --output table 2>/dev/null || echo "   None"

echo ""
