"""
Music Downloader - Get royalty-free romantic/sensuous music

Sources (all FREE for commercial use):
- Incompetech (Kevin MacLeod) - CC BY 3.0
- Pixabay Music - CC0
- Chosic - Free for commercial use

Usage:
    python scripts/music_downloader.py --list
    python scripts/music_downloader.py --download all
    python scripts/music_downloader.py --download sensual_latin
"""
import os
import sys
import argparse
import requests
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MUSIC_DIR

# Curated list of FREE royalty-free romantic/sensuous tracks
MUSIC_TRACKS = {
    "sensual_latin": {
        "name": "Verano Sensual",
        "description": "Latin sensual vibe, perfect for romantic slideshows",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Verano%20Sensual.mp3",
        "duration": "2:30",
        "mood": "sensual, latin, romantic",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    },
    "slow_burn": {
        "name": "Slow Burn",
        "description": "Sultry, slow-building romantic atmosphere",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Slow%20Burn.mp3",
        "duration": "4:25",
        "mood": "sultry, slow, intimate",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    },
    "evening_romance": {
        "name": "Evening of Chaos",
        "description": "Mysterious romantic evening vibes",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Evening%20of%20Chaos.mp3",
        "duration": "3:12",
        "mood": "mysterious, romantic, evening",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    },
    "tender_moment": {
        "name": "Tender",
        "description": "Soft, gentle romantic piano",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Tender.mp3",
        "duration": "2:48",
        "mood": "tender, soft, piano",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    },
    "romantic_night": {
        "name": "Night on the Docks - Sax",
        "description": "Smooth sax for romantic nights",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Night%20on%20the%20Docks%20-%20Sax.mp3",
        "duration": "3:00",
        "mood": "saxophone, jazz, romantic",
        "attribution": "Kevin MacLeod (incompetech.com) CC BY 3.0"
    }
}

# YouTube tracks (use --youtube-audio with these URLs, skip first 10 seconds)
YOUTUBE_TRACKS = {
    "yt_sensual_1": {
        "name": "YouTube Sensual Track 1",
        "url": "https://www.youtube.com/watch?v=cNAo9S8Nr_M",
        "skip_seconds": 10,
        "description": "Sensual romantic track from YouTube"
    },
    "yt_sensual_2": {
        "name": "YouTube Sensual Track 2",
        "url": "https://www.youtube.com/watch?v=KKAWuhSnh6c",
        "skip_seconds": 10,
        "description": "Sensual romantic track from YouTube"
    },
    "yt_sensual_3": {
        "name": "YouTube Sensual Track 3",
        "url": "https://www.youtube.com/watch?v=FmD5rQrXpXU",
        "skip_seconds": 10,
        "description": "Sensual romantic track from YouTube"
    }
}


def download_track(track_id: str, output_dir: str = None) -> Optional[str]:
    """Download a single music track."""
    if track_id not in MUSIC_TRACKS:
        print(f"Unknown track: {track_id}")
        print(f"Available tracks: {', '.join(MUSIC_TRACKS.keys())}")
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
    print("\nAvailable Romantic/Sensuous Music Tracks:")
    print("=" * 60)
    for track_id, track in MUSIC_TRACKS.items():
        print(f"\n  {track_id}")
        print(f"    Name: {track['name']}")
        print(f"    Description: {track['description']}")
        print(f"    Duration: {track['duration']}")
        print(f"    Mood: {track['mood']}")
    print("\n" + "=" * 60)
    print("All tracks are FREE and safe for YouTube monetization")
    print("Attribution required (CC BY 3.0)")


def get_music_path(track_id: str = "sensual_latin") -> Optional[str]:
    """Get path to a music file, downloading if needed."""
    output_path = os.path.join(MUSIC_DIR, f"{track_id}.mp3")

    if os.path.exists(output_path):
        return output_path

    # Try to download
    return download_track(track_id)


def get_attribution(track_id: str) -> str:
    """Get attribution text for a track."""
    if track_id in MUSIC_TRACKS:
        track = MUSIC_TRACKS[track_id]
        return f"Music: {track['name']} by {track['attribution']}"
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Download royalty-free romantic/sensuous music"
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
        # Default: list tracks
        list_tracks()


if __name__ == "__main__":
    main()
