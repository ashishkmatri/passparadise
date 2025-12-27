"""
YouTube Kids Stories Automation - Configuration
"""
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORIES_DIR = os.path.join(BASE_DIR, "stories")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

# Create directories if they don't exist
for dir_path in [STORIES_DIR, OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, MUSIC_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 25  # 25fps works better with Ken Burns zoompan filter
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"

# TTS settings
# en-US-JennyNeural: Clear, friendly female voice (best for kids storytelling)
# Alternative voices: en-US-AriaNeural, en-US-SaraNeural, en-GB-SoniaNeural
TTS_VOICE = "en-US-JennyNeural"
TTS_RATE = "+0%"  # Normal speed (avoid distortion from slowing down)
TTS_PITCH = "+0Hz"  # Normal pitch

# Image settings
IMAGE_FORMAT = "png"
PLACEHOLDER_BG_COLOR = (25, 25, 50)  # Dark blue night sky
STAR_COLOR = (255, 255, 200)  # Warm yellow stars

# Timing
INTRO_DURATION = 3  # seconds
OUTRO_DURATION = 4  # seconds
MIN_SCENE_DURATION = 4  # minimum seconds per scene
WORDS_PER_SECOND = 2.5  # reading speed for duration calculation

# Intro/Outro text
INTRO_TEMPLATE = "{title}"
OUTRO_TEXT = "The End"
SUBSCRIBE_CTA = "Subscribe for more stories!"

# ============================================================
# VIDEO EFFECTS SETTINGS
# ============================================================

# Ken Burns effect (subtle zoom/pan on images)
KEN_BURNS_ENABLED = True

# Crossfade transitions between scenes
CROSSFADE_ENABLED = True
CROSSFADE_DURATION = 0.3  # seconds

# Background music settings
BACKGROUND_MUSIC_ENABLED = True
BACKGROUND_MUSIC_VOLUME = 0.15  # 15% volume (soft)
DEFAULT_MUSIC_FILE = os.path.join(MUSIC_DIR, "kids_adventure.mp3")

# ============================================================
# AI IMAGE GENERATION (Hugging Face - FREE)
# ============================================================

# Hugging Face token (optional - works without, just slower)
# Sign up free at: https://huggingface.co
# Get token from: https://huggingface.co/settings/tokens
HF_API_TOKEN = os.environ.get('HF_API_TOKEN', 'your_hf_token_here')

# Enable/disable AI image generation
# True = use Hugging Face Stable Diffusion (free, unlimited)
# False = use placeholder images (faster, no API calls)
USE_AI_IMAGES = True
