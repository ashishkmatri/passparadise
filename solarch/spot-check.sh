#!/bin/bash
# My first instance type script

INSTANCE_TYPE="t3.medium"
REGION="us-east-1"

aws ec2 describe-spot-price-history --instance-types $INSTANCE_TYPE --region $REGION --product-descriptions "Linux/UNIX" --max-items 3  --query 'SpotPriceHistory[*].[AvailablityZone, SpotPrice, Timestamp]' --output table
