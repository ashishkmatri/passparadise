#!/bin/bash
#Error handling for spot instance script
INSTANCE_TYPE=${1:-"t3.medium"}
REGION=${2:-"us-east-1"}
echo "Checking Spot Prices history for $INSTANCE_TYPE in region $REGION"


RESULT=$(aws ec2 describe-spot-price-history --instance-types $INSTANCE_TYPE --region $REGION --product-descriptions "Linux/UNIX" \
    --max-items 5 \
    --query 'SpotPriceHistory[*].[AvailabllityZone, SpotPrice, Timestamp]' \
    --output table 2>&1)

if [ $? -eq 0 ]; then
    echo "$RESULT"
else
    echo "Error: could not fetch spot price history"
    exit 1
fi

