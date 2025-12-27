"""
Background Music Downloader - Get royalty-free music for YouTube videos

Sources (all FREE for commercial use):
- Pixabay Music: https://pixabay.com/music/
- No-copyright music collections

Usage:
    python scripts/music_downloader.py --list          # Show available tracks
    python scripts/music_downloader.py --download all  # Download all tracks
    python scripts/music_downloader.py --download kids_adventure
"""
import os
import sys
import argparse
import requests
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MUSIC_DIR

# Curated list of FREE royalty-free tracks suitable for kids content
# These are from Free Music Archive, Incompetech, and other CC0/CC-BY sources
# All tracks are safe for YouTube monetization

MUSIC_TRACKS = {
    "kids_adventure": {
        "name": "Kids Adventure",
        "description": "Upbeat, playful track perfect for story adventures",
        # Kevin MacLeod - Carefree (CC BY 3.0) - famous royalty-free composer
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3",
        "duration": "2:15",
        "mood": "happy, playful",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    },
    "gentle_lullaby": {
        "name": "Gentle Lullaby",
        "description": "Soft, calming music for bedtime stories",
        # Kevin MacLeod - Dreamlike (CC BY 3.0)
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dreamlike.mp3",
        "duration": "2:48",
        "mood": "calm, soothing",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    },
    "magical_forest": {
        "name": "Magical Forest",
        "description": "Whimsical, enchanting music for fantasy stories",
        # Kevin MacLeod - Enchanted Valley (CC BY 3.0)
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Enchanted%20Valley.mp3",
        "duration": "2:33",
        "mood": "magical, wonder",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    },
    "happy_day": {
        "name": "Happy Day",
        "description": "Cheerful tune for fun stories",
        # Kevin MacLeod - Happy Boy End Theme (CC BY 3.0)
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Happy%20Boy%20End%20Theme.mp3",
        "duration": "0:41",
        "mood": "cheerful, light",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    },
    "peaceful_garden": {
        "name": "Peaceful Garden",
        "description": "Gentle music for emotional story moments",
        # Kevin MacLeod - Garden Music (CC BY 3.0)
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Garden%20Music.mp3",
        "duration": "3:26",
        "mood": "emotional, peaceful",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    }
}


def download_track(track_id: str, output_dir: str = None) -> Optional[str]:
    """Download a single music track."""
    if track_id not in MUSIC_TRACKS:
        print(f"Unknown track: {track_id}")
        return None

    track = MUSIC_TRACKS[track_id]
    output_dir = output_dir or MUSIC_DIR
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{track_id}.mp3")

    if os.path.exists(output_path):
        print(f"Already exists: {track['name']}")
        return output_path

    print(f"Downloading: {track['name']}...")

    try:
        response = requests.get(track['url'], timeout=60, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"  Saved: {output_path}")
            return output_path
        else:
            print(f"  Download failed: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"  Download error: {e}")
        return None


def download_all(output_dir: str = None) -> dict:
    """Download all music tracks."""
    results = {}
    for track_id in MUSIC_TRACKS:
        path = download_track(track_id, output_dir)
        results[track_id] = path
    return results


def list_tracks():
    """List all available tracks."""
    print("\nAvailable Background Music Tracks:")
    print("=" * 60)
    for track_id, track in MUSIC_TRACKS.items():
        print(f"\n  {track_id}")
        print(f"    Name: {track['name']}")
        print(f"    Description: {track['description']}")
        print(f"    Duration: {track['duration']}")
        print(f"    Mood: {track['mood']}")
    print("\n" + "=" * 60)
    print("All tracks are FREE and safe for YouTube monetization")


def get_music_path(track_id: str = "kids_adventure") -> Optional[str]:
    """Get path to a music file, downloading if needed."""
    output_path = os.path.join(MUSIC_DIR, f"{track_id}.mp3")

    if os.path.exists(output_path):
        return output_path

    # Try to download
    return download_track(track_id)


def main():
    parser = argparse.ArgumentParser(
        description="Download royalty-free background music"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available tracks"
    )
    parser.add_argument(
        "--download", "-d",
        help="Download track(s): track_id or 'all'"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory (default: assets/music)"
    )

    args = parser.parse_args()

    if args.list:
        list_tracks()
    elif args.download:
        if args.download.lower() == "all":
            results = download_all(args.output)
            print(f"\nDownloaded {sum(1 for v in results.values() if v)} tracks")
        else:
            download_track(args.download, args.output)
    else:
        # Default: download the default track
        print("Downloading default track (kids_adventure)...")
        download_track("kids_adventure")
        print("\nUse --list to see all available tracks")
        print("Use --download all to download all tracks")


if __name__ == "__main__":
    main()
