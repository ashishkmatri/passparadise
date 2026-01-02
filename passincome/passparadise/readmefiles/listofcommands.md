# PassParadise - Command Reference

## Quick Start

```bash
cd /home/ashish/pers/passincome/passparadise/paradise-automation
```

---

## 1. Video Generation

### Generate video with curated music (recommended)
```bash
python generate.py /path/to/images/ --music sensual_latin
```

### Generate with all curated tracks
```bash
python generate.py /path/to/images/ --music sensual_latin
python generate.py /path/to/images/ --music slow_burn
python generate.py /path/to/images/ --music evening_romance
python generate.py /path/to/images/ --music tender_moment
python generate.py /path/to/images/ --music romantic_night
```

### Generate with your own music file
```bash
python generate.py /path/to/images/ --music-file /path/to/song.mp3
```

### Generate with YouTube audio (may require authentication)
```bash
# Default: skips first 10 seconds
python generate.py /path/to/images/ -y "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom skip duration
python generate.py /path/to/images/ -y "https://youtube.com/watch?v=..." --skip 15
```

### Custom output path
```bash
python generate.py /path/to/images/ --music sensual_latin --output /path/to/output/my_video.mp4
```

### Sort images differently
```bash
# By filename (alphabetical)
python generate.py /path/to/images/ --music sensual_latin --sort filename

# Random order
python generate.py /path/to/images/ --music sensual_latin --sort random

# By date modified (default)
python generate.py /path/to/images/ --music sensual_latin --sort date_modified
```

### Disable effects (no Ken Burns, no crossfade)
```bash
python generate.py /path/to/images/ --music sensual_latin --no-effects
```

### List available music tracks
```bash
python generate.py --list-music
```

---

## 2. Music Management

### List all curated tracks
```bash
python scripts/music_downloader.py --list
```

### Download a specific track
```bash
python scripts/music_downloader.py --download sensual_latin
python scripts/music_downloader.py --download slow_burn
```

### Download all curated tracks
```bash
python scripts/music_downloader.py --download all
```

---

## 3. YouTube Audio Extraction

> **Note:** YouTube may require authentication. Curated tracks are recommended.

### Extract audio from YouTube (standalone)
```bash
python scripts/youtube_audio.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Extract with custom output path
```bash
python scripts/youtube_audio.py "https://youtube.com/..." --output /path/to/audio.mp3
```

### Get video info without downloading
```bash
python scripts/youtube_audio.py "https://youtube.com/..." --info
```

---

## 4. Image Loading (Testing)

### List images in a folder
```bash
python scripts/image_loader.py /path/to/images/
```

### List with different sorting
```bash
python scripts/image_loader.py /path/to/images/ --sort filename
python scripts/image_loader.py /path/to/images/ --sort random
```

---

## 5. Server Management

### Create/Start EC2 server
```bash
cd /home/ashish/pers/passincome/youtube-terraform
AWS_PROFILE=personal terraform apply -auto-approve
```

### Get server IP after creation
```bash
cd /home/ashish/pers/passincome/youtube-terraform
terraform output public_ip
```

### SSH into server
```bash
ssh -i ~/.ssh/youtube-ec2-key ubuntu@<IP_ADDRESS>
```

### Destroy server (stop all costs)
```bash
cd /home/ashish/pers/passincome/youtube-terraform
AWS_PROFILE=personal terraform destroy -auto-approve
```

---

## 6. File Transfer

### Upload images to server (from WSL)
```bash
scp -i ~/.ssh/youtube-ec2-key -r /mnt/c/Users/ashis/OneDrive/Pictures/seart/29dec25/* ubuntu@<IP>:/data/images/29dec25/
```

### Download video from server (to WSL)
```bash
scp -i ~/.ssh/youtube-ec2-key ubuntu@<IP>:/data/paradise-automation/output/*.mp4 /mnt/c/Users/ashis/OneDrive/Pictures/seart/outputs/
```

### Upload images (from Windows PowerShell)
```powershell
scp -i C:\Users\ashis\.ssh\youtube-ec2-key -r "C:\Users\ashis\OneDrive\Pictures\seart\29dec25\*" ubuntu@<IP>:/data/images/29dec25/
```

### Download video (to Windows)
```powershell
scp -i C:\Users\ashis\.ssh\youtube-ec2-key ubuntu@<IP>:/data/paradise-automation/output/*.mp4 "C:\Users\ashis\OneDrive\Pictures\seart\outputs\"
```

---

## 7. Install Dependencies

### On EC2 server
```bash
cd /data/paradise-automation
pip install -r requirements.txt
pip install yt-dlp
```

### System dependencies (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install -y ffmpeg python3-pip
```

---

## Full Example Workflow

```bash
# 1. Create server (from local WSL)
cd /home/ashish/pers/passincome/youtube-terraform
AWS_PROFILE=personal terraform apply -auto-approve

# 2. Get IP address
IP=$(terraform output -raw public_ip)
echo "Server IP: $IP"

# 3. Wait for server to initialize (~2-3 min), then SSH
ssh -i ~/.ssh/youtube-ec2-key ubuntu@$IP

# 4. On server: Mount data volume (if first time after create)
sudo mkdir -p /data && sudo mount /dev/nvme1n1 /data

# 5. On server: Create images folder
mkdir -p /data/images/29dec25

# 6. From local: Upload images
scp -i ~/.ssh/youtube-ec2-key -r /mnt/c/Users/ashis/OneDrive/Pictures/seart/29dec25/* ubuntu@$IP:/data/images/29dec25/

# 7. On server: Generate video
cd /data/paradise-automation
python3 generate.py /data/images/29dec25 --music sensual_latin

# 8. From local: Download video
scp -i ~/.ssh/youtube-ec2-key ubuntu@$IP:/data/paradise-automation/output/*.mp4 /mnt/c/Users/ashis/OneDrive/Pictures/seart/outputs/

# 9. Destroy server when done (saves money!)
cd /home/ashish/pers/passincome/youtube-terraform
AWS_PROFILE=personal terraform destroy -auto-approve
```

---

## Available Curated Tracks (Royalty-Free)

| Track ID | Name | Mood | Source |
|----------|------|------|--------|
| sensual_latin | Verano Sensual | Latin, sensual | Incompetech (CC BY 3.0) |
| slow_burn | Slow Burn | Sultry, intimate | Incompetech (CC BY 3.0) |
| evening_romance | Evening of Chaos | Mysterious, romantic | Incompetech (CC BY 3.0) |
| tender_moment | Tender | Soft, piano | Incompetech (CC BY 3.0) |
| romantic_night | Night on the Docks - Sax | Saxophone, jazz | Incompetech (CC BY 3.0) |

**Attribution required:** Music by Kevin MacLeod (incompetech.com) CC BY 3.0

---

## Video Settings

| Setting | Value |
|---------|-------|
| Resolution | 1920x1080 (Full HD) |
| Duration per image | 7 seconds |
| Ken Burns effect | Enabled (4% zoom) |
| Crossfade | 0.5 seconds |
| Audio format | AAC 192kbps |

---

## Cost Summary

| Resource | Cost |
|----------|------|
| EC2 Spot (t3.medium) | ~₹0.50/hour |
| EBS Volume (30GB) | ~₹2.40/month |
| Data Transfer | ~₹0.75/GB (outbound) |
| **Per video (~5 min runtime)** | **~₹0.04** |

**Important:** Always destroy the server when not in use to avoid charges!
