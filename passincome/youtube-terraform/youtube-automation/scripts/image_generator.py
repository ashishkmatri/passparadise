"""
Image Generator - AI-generated images using Hugging Face (FREE)

Hugging Face Inference API: Completely FREE, no limits
Uses Stable Diffusion models for kids-friendly illustrations.

Setup:
    1. Sign up at https://huggingface.co (free)
    2. Get API token from https://huggingface.co/settings/tokens
    3. Set environment variable: export HF_API_TOKEN=your_token

Note: Works without token too (slower, rate-limited)
"""
import os
import sys
import time
import random
import requests
from typing import List, Tuple, Optional

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import HF_API_TOKEN
except ImportError:
    HF_API_TOKEN = None

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from io import BytesIO

# Hugging Face API settings
# Using the standard inference API endpoint
HF_API_URL = "https://api-inference.huggingface.co/models"
# Using SDXL-Lightning - fast and reliable for image generation
HF_MODEL = "ByteDance/SDXL-Lightning"

# Kids-friendly style prompt suffix
STYLE_SUFFIX = (
    "children's book illustration style, cute and friendly, "
    "soft pastel colors, whimsical, age-appropriate for toddlers, "
    "warm lighting, safe and comforting atmosphere, "
    "pixar style, dreamworks animation style, high quality"
)

# Negative prompt to ensure kid-safe content
NEGATIVE_PROMPT = "scary, dark, violence, blood, horror, adult content, nsfw, realistic, photo"


def create_starry_background(
    width: int = 1920,
    height: int = 1080,
    bg_color: Tuple[int, int, int] = (15, 15, 40),
    num_stars: int = 200
) -> Image.Image:
    """Create a starry night sky background."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Add gradient (darker at top, slightly lighter at bottom)
    for y in range(height):
        factor = y / height * 0.3
        color = tuple(min(255, int(c + c * factor)) for c in bg_color)
        draw.line([(0, y), (width, y)], fill=color)

    # Add stars
    for _ in range(num_stars):
        x = random.randint(0, width)
        y = random.randint(0, int(height * 0.7))  # Stars mostly in upper portion
        size = random.choice([1, 1, 1, 2, 2, 3])  # Most stars are small
        brightness = random.randint(180, 255)
        color = (brightness, brightness, min(255, brightness + 20))  # Slight yellow tint

        if size == 1:
            draw.point((x, y), fill=color)
        else:
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color)

    return img


def add_text_to_image(
    img: Image.Image,
    text: str,
    position: str = "center",
    font_size: int = 72,
    color: Tuple[int, int, int] = (255, 255, 255)
) -> Image.Image:
    """Add text to an image."""
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Get text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate position
    if position == "center":
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2
    elif position == "top":
        x = (img.width - text_width) // 2
        y = 100
    elif position == "bottom":
        x = (img.width - text_width) // 2
        y = img.height - text_height - 100
    else:
        x, y = 100, 100

    # Add shadow for better visibility
    shadow_offset = 3
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=color)

    return img


def create_scene_placeholder(
    scene_number: int,
    image_prompt: str,
    width: int = 1920,
    height: int = 1080,
    output_path: str = None
) -> Image.Image:
    """
    Create a placeholder image for a scene.
    Shows the scene prompt text on a starry background.
    """
    img = create_starry_background(width, height)

    # Add scene number
    img = add_text_to_image(img, f"Scene {scene_number}", position="top", font_size=48, color=(200, 200, 255))

    # Add image prompt (truncated if too long)
    prompt_display = image_prompt[:80] + "..." if len(image_prompt) > 80 else image_prompt
    img = add_text_to_image(img, prompt_display, position="center", font_size=36, color=(255, 255, 200))

    if output_path:
        img.save(output_path)

    return img


def create_title_card(
    title: str,
    width: int = 1920,
    height: int = 1080,
    output_path: str = None
) -> Image.Image:
    """Create an intro title card with animated-style starry background."""
    img = create_starry_background(width, height, num_stars=300)

    # Add a subtle glow in the center
    center_glow = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(center_glow)
    for r in range(300, 0, -5):
        alpha = int(30 * (r / 300))
        color = (alpha, alpha, alpha + 10)
        draw.ellipse([width//2 - r, height//2 - r, width//2 + r, height//2 + r], fill=color)

    img = Image.blend(img, center_glow, 0.3)

    # Add title
    img = add_text_to_image(img, title, position="center", font_size=80, color=(255, 255, 230))

    if output_path:
        img.save(output_path)

    return img


def create_outro_card(
    width: int = 1920,
    height: int = 1080,
    output_path: str = None
) -> Image.Image:
    """Create an outro card with 'The End' and subscribe CTA."""
    img = create_starry_background(width, height, num_stars=250)

    # Add "The End"
    img = add_text_to_image(img, "The End", position="center", font_size=96, color=(255, 255, 230))

    # Add subscribe CTA
    img = add_text_to_image(img, "Subscribe for more stories!", position="bottom", font_size=42, color=(200, 230, 255))

    if output_path:
        img.save(output_path)

    return img


# ============================================================
# Hugging Face API Functions (FREE)
# ============================================================

def get_api_token() -> Optional[str]:
    """Get Hugging Face API token from config or environment."""
    token = HF_API_TOKEN or os.environ.get('HF_API_TOKEN')
    return token if token and token != 'your_hf_token_here' else None


def hf_generate_image(
    prompt: str,
    output_path: str,
    max_retries: int = 3
) -> Optional[str]:
    """
    Generate image using Hugging Face Inference API (FREE).

    Args:
        prompt: Image description
        output_path: Where to save the image
        max_retries: Number of retries if model is loading

    Returns:
        Path to generated image or None if failed
    """
    headers = {}
    token = get_api_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Enhance prompt with kids-friendly style
    full_prompt = f"{prompt}, {STYLE_SUFFIX}"

    payload = {
        "inputs": full_prompt,
        "parameters": {
            "negative_prompt": NEGATIVE_PROMPT,
            "guidance_scale": 7.5,
            "num_inference_steps": 30
        }
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{HF_API_URL}/{HF_MODEL}",
                headers=headers,
                json=payload,
                timeout=120  # Longer timeout for image generation
            )

            if response.status_code == 200:
                # Response is the image bytes directly
                img = Image.open(BytesIO(response.content))
                img.save(output_path)
                return output_path

            elif response.status_code == 503:
                # Model is loading, wait and retry
                wait_time = response.json().get('estimated_time', 20)
                print(f"    Model loading, waiting {wait_time:.0f}s...")
                time.sleep(min(wait_time, 60))
                continue

            elif response.status_code == 429:
                # Rate limited, wait and retry
                print(f"    Rate limited, waiting 30s...")
                time.sleep(30)
                continue

            else:
                print(f"  HF API error: {response.status_code}")
                try:
                    print(f"    {response.json()}")
                except:
                    pass
                return None

        except Exception as e:
            print(f"  HF API error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            return None

    return None


def generate_scene_image(
    scene_number: int,
    image_prompt: str,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    use_ai: bool = True
) -> str:
    """
    Generate scene image - tries Hugging Face first, falls back to placeholder.

    Args:
        scene_number: Scene index for display
        image_prompt: Description of the scene
        output_path: Where to save the image
        width: Video width
        height: Video height
        use_ai: Whether to try AI generation first

    Returns:
        Path to generated image
    """
    if use_ai:
        print(f"  Generating AI image for scene {scene_number}...")

        result = hf_generate_image(image_prompt, output_path)

        if result:
            # Scale to video resolution
            img = Image.open(result)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img.save(output_path)
            print(f"  AI image generated for scene {scene_number}")
            return output_path
        else:
            print(f"  AI failed, using placeholder for scene {scene_number}")

    # Fallback to placeholder
    create_scene_placeholder(scene_number, image_prompt, width, height, output_path)
    return output_path


def generate_title_image(
    title: str,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    use_ai: bool = True
) -> str:
    """Generate title/intro image with AI or fallback to styled placeholder."""
    if use_ai:
        print(f"  Generating AI intro image...")

        # Create a title-appropriate prompt
        title_prompt = (
            f"Beautiful title card for children's story called '{title}', "
            f"magical sparkles, storybook cover style, enchanting"
        )

        result = hf_generate_image(title_prompt, output_path)

        if result:
            # Scale and add title text overlay
            img = Image.open(result)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img = add_text_to_image(img, title, position="center", font_size=80, color=(255, 255, 230))
            img.save(output_path)
            print(f"  AI intro image generated")
            return output_path

    # Fallback
    create_title_card(title, width, height, output_path)
    return output_path


def generate_outro_image(
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    use_ai: bool = True
) -> str:
    """Generate outro image with AI or fallback to styled placeholder."""
    if use_ai:
        print(f"  Generating AI outro image...")

        outro_prompt = (
            "Magical 'The End' storybook ending scene, "
            "happy stars twinkling, dreamy clouds, soft sunset colors"
        )

        result = hf_generate_image(outro_prompt, output_path)

        if result:
            img = Image.open(result)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img = add_text_to_image(img, "The End", position="center", font_size=96, color=(255, 255, 230))
            img = add_text_to_image(img, "Subscribe for more stories!", position="bottom", font_size=42, color=(200, 230, 255))
            img.save(output_path)
            print(f"  AI outro image generated")
            return output_path

    # Fallback
    create_outro_card(width, height, output_path)
    return output_path


def generate_all_images(
    scenes: List[dict],
    title: str,
    output_dir: str,
    width: int = 1920,
    height: int = 1080,
    use_ai: bool = True
) -> dict:
    """
    Generate all images for a story (intro, scenes, outro).

    Uses Leonardo.ai for AI-generated images if API key is set,
    otherwise falls back to placeholder images.

    Args:
        scenes: List of scene dictionaries with 'image_prompt'
        title: Story title for intro card
        output_dir: Where to save images
        width: Video width
        height: Video height
        use_ai: Whether to try AI generation (default True)

    Returns:
        {
            'intro': path,
            'scenes': [paths...],
            'outro': path
        }
    """
    os.makedirs(output_dir, exist_ok=True)

    result = {
        'intro': None,
        'scenes': [],
        'outro': None
    }

    # Check if AI is available (HF works without token, just slower)
    ai_available = use_ai
    if ai_available:
        token = get_api_token()
        if token:
            print("Hugging Face token found - using AI image generation (faster)")
        else:
            print("Using Hugging Face AI (no token - may be slower)")
            print("  Tip: Set HF_API_TOKEN for faster generation")
    else:
        print("AI disabled - using placeholder images")

    # Create intro
    intro_path = os.path.join(output_dir, "intro.png")
    generate_title_image(title, intro_path, width, height, use_ai=ai_available)
    result['intro'] = intro_path

    # Create scene images
    for i, scene in enumerate(scenes):
        scene_path = os.path.join(output_dir, f"scene_{i:02d}.png")
        generate_scene_image(i + 1, scene['image_prompt'], scene_path, width, height, use_ai=ai_available)
        result['scenes'].append(scene_path)

    # Create outro
    outro_path = os.path.join(output_dir, "outro.png")
    generate_outro_image(outro_path, width, height, use_ai=ai_available)
    result['outro'] = outro_path

    print(f"Generated {len(result['scenes']) + 2} images total")
    return result


if __name__ == "__main__":
    # Test image generation
    test_scenes = [
        {'image_prompt': 'A dark night sky filled with twinkling stars'},
        {'image_prompt': 'A tiny star with a sad face, smaller than all other stars'},
        {'image_prompt': 'A little girl looking out her bedroom window at the stars'}
    ]

    output = generate_all_images(test_scenes, "The Little Star", "./test_images")
    print(f"\nGenerated images:")
    print(f"  Intro: {output['intro']}")
    print(f"  Scenes: {len(output['scenes'])} images")
    print(f"  Outro: {output['outro']}")
