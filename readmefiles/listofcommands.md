# PassParadise - Command Reference

## Quick Start

```bash
cd /home/ashish/pers/passincome/passparadise/paradise-automation
```

---

## 1. Video Generation

### Generate video with YouTube audio (default: skips first 10 sec)
```bash
python generate.py /path/to/images/ --youtube-audio "https://www.youtube.com/watch?v=cNAo9S8Nr_M"
```

### Generate with specific YouTube URL
```bash
# Track 1
python generate.py /path/to/images/ -y "https://www.youtube.com/watch?v=cNAo9S8Nr_M"

# Track 2
python generate.py /path/to/images/ -y "https://www.youtube.com/watch?v=KKAWuhSnh6c"

# Track 3
python generate.py /path/to/images/ -y "https://www.youtube.com/watch?v=FmD5rQrXpXU"
```

### Custom skip duration (e.g., 15 seconds)
```bash
python generate.py /path/to/images/ -y "https://youtube.com/watch?v=..." --skip 15
```

### Generate with curated music tracks
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

### Custom output path
```bash
python generate.py /path/to/images/ -y "URL" --output /path/to/output/my_video.mp4
```

### Sort images differently
```bash
# By filename (alphabetical)
python generate.py /path/to/images/ -y "URL" --sort filename

# Random order
python generate.py /path/to/images/ -y "URL" --sort random

# By date modified (default)
python generate.py /path/to/images/ -y "URL" --sort date_modified
```

### Disable effects (no Ken Burns, no crossfade)
```bash
python generate.py /path/to/images/ -y "URL" --no-effects
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

## 5. Server Management (from youtube-terraform folder)

### Start EC2 server
```bash
cd /home/ashish/pers/passincome/youtube-terraform
./start.sh
```

### Stop EC2 server (save costs)
```bash
./stop.sh
```

### Check server status
```bash
./status.sh
```

### SSH into server
```bash
ssh -i ~/.ssh/youtube-key ubuntu@<IP_ADDRESS>
```

### Backup and destroy (for long breaks)
```bash
./backup-and-destroy.sh
```

### Restore from backup
```bash
./restore.sh
```

---

## 6. Install Dependencies

### On local machine or EC2
```bash
cd /home/ashish/pers/passincome/passparadise/paradise-automation
pip install -r requirements.txt
```

### System dependencies (Ubuntu/Debian)
```bash
sudo apt install ffmpeg python3-pip
```

---

## Full Example Workflow

```bash
# 1. Start server
cd /home/ashish/pers/passincome/youtube-terraform
./start.sh

# 2. SSH into server
ssh -i ~/.ssh/youtube-key ubuntu@<IP>

# 3. Navigate to project
cd /path/to/passparadise/paradise-automation

# 4. Generate video
python generate.py ~/my_images/ -y "https://www.youtube.com/watch?v=cNAo9S8Nr_M"

# 5. Download generated video (from local machine)
scp -i ~/.ssh/youtube-key ubuntu@<IP>:/path/to/output/*.mp4 ~/Downloads/

# 6. Stop server when done
./stop.sh
```

---

## Available YouTube Tracks (Pre-configured)

| ID | URL | Description |
|----|-----|-------------|
| yt_sensual_1 | https://www.youtube.com/watch?v=cNAo9S8Nr_M | Sensual Track 1 |
| yt_sensual_2 | https://www.youtube.com/watch?v=KKAWuhSnh6c | Sensual Track 2 |
| yt_sensual_3 | https://www.youtube.com/watch?v=FmD5rQrXpXU | Sensual Track 3 |

---

## Available Curated Tracks (Royalty-Free)

| Track ID | Name | Mood |
|----------|------|------|
| sensual_latin | Verano Sensual | Latin, sensual |
| slow_burn | Slow Burn | Sultry, intimate |
| evening_romance | Evening of Chaos | Mysterious, romantic |
| tender_moment | Tender | Soft, piano |
| romantic_night | Night on the Docks - Sax | Saxophone, jazz |

---

## Cost Summary

| Task | Time | Cost (Spot) |
|------|------|-------------|
| 1 video (t3.medium) | ~5 min | ₹0.12 |
| AI image generation (g4dn.xlarge) | ~5 min | ₹1-2 |
