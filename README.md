# PassParadise - Music Video Creator

Create slideshow music videos from images with audio.

## Features
- Supports JPG, JPEG, PNG images
- Auto-shuffles images (no same folder back-to-back)
- Customizable duration per image
- Customizable resolution
- Romantic/sensuous content for mature audience (16+)

## Local Usage

### Requirements
- Python 3.8+
- FFmpeg installed

### Install FFmpeg
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install ffmpeg
```

### Run the script
```bash
python create_music_video.py \
    --images /path/to/images \
    --audio /path/to/audio.mp3 \
    --duration 7 \
    --output my_video.mp4
```

### Options
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --images | -i | Path to images folder | Required |
| --audio | -a | Path to audio file | Required |
| --duration | -d | Seconds per image | 7 |
| --output | -o | Output video path | output_video.mp4 |
| --resolution | -r | Video resolution | 1920:1080 |
| --no-shuffle | | Disable shuffling | False |

### Example
```bash
# 83 images, 7 sec each = ~10 min video
python create_music_video.py -i ./my_images -a ./romantic_music.mp3 -d 7 -o romantic_video.mp4
```

## GitHub Actions Workflow

You can also create videos using GitHub Actions:

1. Go to **Actions** tab in the repository
2. Select **Create Music Video** workflow
3. Click **Run workflow**
4. Provide:
   - URL to zipped images (Google Drive, Dropbox, etc.)
   - URL to audio file
   - Duration per image (default: 7 seconds)
   - Resolution (default: 1920:1080)
5. Download the video from **Artifacts** when complete

## Output
- Format: MP4 (H.264 video, AAC audio)
- Quality: CRF 23 (good quality, reasonable size)
- Audio: 192 kbps AAC
