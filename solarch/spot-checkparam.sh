#!/bin/bash
#Spot instnaces with parameters
INSTANCE_TYPE=${1:-"t3.medium"}
REGION=${2:-"us-east-1"}

echo "Checking Spot Prices history for $INSTANCE_TYPE in region $REGION"

aws ec2 describe-spot-price-history --instance-types $1 --region $2 --product-descriptions "Linux/UNIX" --max-items 3  --query 'SpotPriceHistory[*].[AvailablityZone, SpotPrice, Timestamp]' --output table