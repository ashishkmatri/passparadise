"""
PassParadise - Romantic Image Slideshow Video Generator
Configuration for mature audience (16+)
"""
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
YOUTUBE_MUSIC_DIR = os.path.join(MUSIC_DIR, "youtube")

# Create directories if they don't exist
for dir_path in [OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, MUSIC_DIR, YOUTUBE_MUSIC_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 25
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"

# Image settings
SUPPORTED_IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif')

# Music settings - Full volume (no narration to mix with)
BACKGROUND_MUSIC_VOLUME = 1.0  # 100% volume

# Effects settings
KEN_BURNS_ENABLED = True
CROSSFADE_ENABLED = True
CROSSFADE_DURATION = 0.5  # Longer crossfade for sensual mood

# Duration settings
TARGET_VIDEO_DURATION = 150  # 2.5 minutes default (in seconds)
MIN_IMAGE_DURATION = 3  # Minimum seconds per image
MAX_IMAGE_DURATION = 10  # Maximum seconds per image

# Attribution text (for CC BY licensed music)
ATTRIBUTION_TEMPLATE = """
Music: {title}
{attribution}
"""
