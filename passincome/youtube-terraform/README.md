# 🎬 YouTube Automation - EC2 Terraform

Cost-optimized AWS EC2 setup for YouTube Kids Story automation.

## 💰 Cost Strategy

| State | Monthly Cost | When to Use |
|-------|--------------|-------------|
| **Running** | ~₹3,000 | Actively generating videos |
| **Stopped** | ~₹200 | Taking a break (days) |
| **Destroyed (AMI backup)** | ~₹125 | Not using for weeks/months |

## 📋 Prerequisites

1. **AWS CLI configured**
   ```bash
   aws configure
   # Enter your Access Key, Secret Key, Region: ap-south-1
   ```

2. **Terraform installed**
   ```bash
   # Ubuntu/WSL
   sudo apt update && sudo apt install -y gnupg software-properties-common
   wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
   echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
   sudo apt update && sudo apt install terraform
   ```

3. **SSH key generated**
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/youtube-key
   ```

## 🚀 Initial Setup

### Step 1: Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
aws_region     = "ap-south-1"
instance_type  = "t3.medium"
storage_size   = 30
ssh_public_key = "ssh-ed25519 AAAA... your-email@example.com"  # Paste from: cat ~/.ssh/youtube-key.pub
restore_from_ami = ""
```

### Step 2: Initialize Terraform

```bash
terraform init
```

### Step 3: Create Infrastructure

```bash
terraform apply
```

### Step 4: Connect via SSH

```bash
ssh -i ~/.ssh/youtube-key ubuntu@<PUBLIC_IP>
```

## 📖 Daily Usage

### Check Status
```bash
./status.sh
```

### Start Working (Morning)
```bash
./start.sh
# Connect and generate videos
ssh -i ~/.ssh/youtube-key ubuntu@<IP>
```

### Stop When Done (Night)
```bash
./stop.sh
# Saves ~90% cost!
```

## 💾 Long Break (Weeks/Months)

### Backup and Destroy
```bash
./backup-and-destroy.sh
# Creates AMI backup
# Destroys EC2 + EBS
# Saves ~95% cost!
```

### Restore When Ready
```bash
./restore.sh
# Recreates everything from backup
# All your data and scripts preserved!
```

## 📊 Cost Breakdown

### Running 24/7 (Not Recommended)
| Component | Monthly |
|-----------|---------|
| EC2 t3.medium | ~₹2,500 |
| EBS 30GB | ~₹200 |
| Data Transfer | ~₹300 |
| **Total** | **~₹3,000** |

### Start/Stop Strategy (Recommended)
| Usage | Monthly |
|-------|---------|
| 20 hours compute | ~₹70 |
| EBS 30GB (always) | ~₹200 |
| Data Transfer | ~₹100 |
| **Total** | **~₹370** |

### Backup & Destroy (Minimal)
| Component | Monthly |
|-----------|---------|
| AMI Snapshot | ~₹125 |
| **Total** | **~₹125** |

## 🔧 Useful Commands

```bash
# Check instance state
./status.sh

# SSH into server
ssh -i ~/.ssh/youtube-key ubuntu@$(terraform output -raw public_ip)

# View Terraform outputs
terraform output

# List all backups
aws ec2 describe-images --owners self --region ap-south-1 \
  --query 'Images[*].[ImageId,Name,CreationDate]' --output table

# Delete old backup (to save money)
aws ec2 deregister-image --image-id ami-xxxxx --region ap-south-1
```

## 📁 File Structure

```
youtube-terraform/
├── main.tf                 # Main infrastructure
├── variables.tf            # Variable definitions
├── outputs.tf              # Output values
├── terraform.tfvars        # Your configuration (git-ignored)
├── terraform.tfvars.example
├── start.sh                # Start instance
├── stop.sh                 # Stop instance
├── backup-and-destroy.sh   # Create AMI & destroy
├── restore.sh              # Restore from AMI
├── status.sh               # Check current state
└── README.md               # This file
```

## ⚠️ Important Notes

1. **IP Changes**: When you stop/start, public IP changes. Use `./start.sh` to get new IP.

2. **Data Safety**: 
   - Stop: Data preserved on EBS
   - Destroy: Data preserved in AMI backup

3. **SSH Key**: Keep `~/.ssh/youtube-key` safe. You need it to connect.

4. **Costs**: Always run `./stop.sh` when done working!

## 🆘 Troubleshooting

### "Instance not found"
The instance was destroyed. Run `./restore.sh` to recreate from backup.

### "Permission denied (SSH)"
```bash
chmod 400 ~/.ssh/youtube-key
```

### "Cannot connect"
1. Check instance is running: `./status.sh`
2. Check security group allows your IP
3. Wait 1-2 minutes after start

### "State lock"
```bash
terraform force-unlock <LOCK_ID>
```
