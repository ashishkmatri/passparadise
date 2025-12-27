#!/bin/bash
# =============================================================
# STOP EC2 Instance
# Cost: Stops compute billing, still paying for EBS storage
# Savings: ~90% (only pay ~$2.50/month for storage)
# =============================================================

set -e

echo "🛑 Stopping YouTube Automation Server..."

# Get instance ID from Terraform state
INSTANCE_ID=$(terraform output -raw instance_id 2>/dev/null)

if [ -z "$INSTANCE_ID" ]; then
    echo "❌ No instance found."
    exit 1
fi

# Check current state
STATE=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region ap-south-1 \
    --query 'Reservations[0].Instances[0].State.Name' \
    --output text)

if [ "$STATE" == "stopped" ]; then
    echo "ℹ️  Instance is already stopped."
    exit 0
fi

# Stop instance
aws ec2 stop-instances --instance-ids "$INSTANCE_ID" --region ap-south-1

echo "⏳ Waiting for instance to stop..."
aws ec2 wait instance-stopped --instance-ids "$INSTANCE_ID" --region ap-south-1

echo ""
echo "=============================================="
echo "✅ Instance Stopped!"
echo "=============================================="
echo "Instance ID: $INSTANCE_ID"
echo ""
echo "💰 Cost Savings:"
echo "   ✓ Compute billing STOPPED"
echo "   ✓ Only paying for storage (~₹200/month)"
echo ""
echo "📋 Next Steps:"
echo "   • To resume work: ./start.sh"
echo "   • To save more (destroy): ./backup-and-destroy.sh"
echo "=============================================="
