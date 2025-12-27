#!/bin/bash
# =============================================================
# START EC2 Instance
# Cost: Starts billing for compute
# =============================================================

set -e

echo "🚀 Starting YouTube Automation Server..."

# Get instance ID from Terraform state
INSTANCE_ID=$(terraform output -raw instance_id 2>/dev/null)

if [ -z "$INSTANCE_ID" ]; then
    echo "❌ No instance found. Run 'terraform apply' first."
    exit 1
fi

# Start instance
aws ec2 start-instances --instance-ids "$INSTANCE_ID" --region ap-south-1

echo "⏳ Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region ap-south-1

# Get new public IP
NEW_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region ap-south-1 \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo "=============================================="
echo "✅ Instance Started!"
echo "=============================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP:   $NEW_IP"
echo ""
echo "SSH Command:"
echo "ssh -i ~/.ssh/youtube-key ubuntu@$NEW_IP"
echo ""
echo "💰 Billing has started for compute!"
echo "   Run './stop.sh' when done to save money."
echo "=============================================="
