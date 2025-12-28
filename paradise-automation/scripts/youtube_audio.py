"""
YouTube Audio Extractor - Download audio from YouTube using yt-dlp

For extracting audio from "No Copyright Music" YouTube videos.

Usage:
    python scripts/youtube_audio.py "https://youtube.com/watch?v=..."
    python scripts/youtube_audio.py "https://youtube.com/watch?v=..." --output my_audio.mp3
"""
import os
import sys
import subprocess
import hashlib
import argparse
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import YOUTUBE_MUSIC_DIR


def get_video_id(url: str) -> str:
    """Extract video ID from YouTube URL for caching."""
    # Simple extraction - handles most common formats
    if "v=" in url:
        return url.split("v=")[1].split("&")[0][:11]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0][:11]
    else:
        # Fallback: hash the URL
        return hashlib.md5(url.encode()).hexdigest()[:11]


def extract_audio(
    youtube_url: str,
    output_path: str = None,
    cache_dir: str = None,
    skip_seconds: float = 0
) -> Optional[str]:
    """
    Extract audio from YouTube video using yt-dlp.

    Args:
        youtube_url: YouTube video URL
        output_path: Custom output path (optional)
        cache_dir: Directory to cache downloads (default: assets/music/youtube/)
        skip_seconds: Skip first N seconds of audio (default: 0)

    Returns:
        Path to extracted audio file, or None on failure
    """
    cache_dir = cache_dir or YOUTUBE_MUSIC_DIR
    os.makedirs(cache_dir, exist_ok=True)

    # Check cache first (include skip in cache key if used)
    video_id = get_video_id(youtube_url)
    cache_suffix = f"_skip{int(skip_seconds)}" if skip_seconds > 0 else ""
    cached_path = os.path.join(cache_dir, f"{video_id}{cache_suffix}.mp3")

    if os.path.exists(cached_path):
        print(f"Using cached audio: {cached_path}")
        if output_path and output_path != cached_path:
            import shutil
            shutil.copy(cached_path, output_path)
            return output_path
        return cached_path

    # Download with yt-dlp
    print(f"Extracting audio from: {youtube_url}")
    if skip_seconds > 0:
        print(f"  Skipping first {skip_seconds} seconds")

    # First download to temp file
    temp_path = os.path.join(cache_dir, f"{video_id}_temp.%(ext)s")

    cmd = [
        'yt-dlp',
        '-x',  # Extract audio
        '--audio-format', 'mp3',
        '--audio-quality', '0',  # Best quality
        '-o', temp_path,
        '--no-playlist',  # Don't download playlists
        youtube_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"yt-dlp error: {result.stderr}")
            return None

        # Check if file was created
        temp_mp3 = os.path.join(cache_dir, f"{video_id}_temp.mp3")
        if not os.path.exists(temp_mp3):
            print(f"Error: Expected file not found at {temp_mp3}")
            return None

        # If skip_seconds > 0, trim the audio using ffmpeg
        if skip_seconds > 0:
            print(f"  Trimming: skipping first {skip_seconds}s...")
            trim_cmd = [
                'ffmpeg', '-y',
                '-i', temp_mp3,
                '-ss', str(skip_seconds),  # Skip first N seconds
                '-c:a', 'libmp3lame',
                '-b:a', '192k',
                cached_path
            ]
            trim_result = subprocess.run(trim_cmd, capture_output=True, text=True)
            if trim_result.returncode != 0:
                print(f"  Trim failed: {trim_result.stderr}")
                # Fallback: use untrimmed
                import shutil
                shutil.move(temp_mp3, cached_path)
            else:
                os.remove(temp_mp3)
        else:
            import shutil
            shutil.move(temp_mp3, cached_path)

        print(f"Audio saved: {cached_path}")

        if output_path and output_path != cached_path:
            import shutil
            shutil.copy(cached_path, output_path)
            return output_path

        return cached_path

    except subprocess.TimeoutExpired:
        print("Download timed out (5 min limit)")
        return None
    except FileNotFoundError:
        print("Error: yt-dlp not installed. Install with: pip install yt-dlp")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_video_info(youtube_url: str) -> Optional[dict]:
    """Get video info without downloading."""
    cmd = [
        'yt-dlp',
        '--dump-json',
        '--no-playlist',
        youtube_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        return None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Extract audio from YouTube videos"
    )
    parser.add_argument(
        "url",
        help="YouTube video URL"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: cache with video ID)"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show video info without downloading"
    )

    args = parser.parse_args()

    if args.info:
        info = get_video_info(args.url)
        if info:
            print(f"Title: {info.get('title')}")
            print(f"Duration: {info.get('duration')}s")
            print(f"Channel: {info.get('channel')}")
            print(f"License: {info.get('license', 'Unknown')}")
        else:
            print("Could not get video info")
    else:
        path = extract_audio(args.url, args.output)
        if path:
            print(f"\nSuccess! Audio saved to: {path}")
        else:
            print("\nFailed to extract audio")
            sys.exit(1)


if __name__ == "__main__":
    main()
