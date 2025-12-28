#!/usr/bin/env python3
"""
PassParadise - Romantic Image Slideshow Video Generator
Main Pipeline: Images + Music = Video

Features:
- Ken Burns effect (subtle zoom on images)
- Crossfade transitions between images
- Background music (full volume)
- Auto-calculate duration per image from music length

Usage:
    python pipeline.py /path/to/images/
    python pipeline.py /path/to/images/ --music slow_burn
    python pipeline.py /path/to/images/ --youtube-audio "https://youtube.com/..."
"""
import os
import sys
import argparse
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    OUTPUT_DIR, TEMP_DIR, VIDEO_WIDTH, VIDEO_HEIGHT,
    KEN_BURNS_ENABLED, CROSSFADE_ENABLED, CROSSFADE_DURATION,
    BACKGROUND_MUSIC_VOLUME
)
from scripts.image_loader import load_images_from_folder
from scripts.video_assembler import assemble_slideshow, get_audio_duration
from scripts.music_downloader import get_music_path, get_attribution, MUSIC_TRACKS
from scripts.youtube_audio import extract_audio


def generate_video(
    images_folder: str,
    music_track: str = None,
    youtube_url: str = None,
    music_file: str = None,
    output_path: str = None,
    use_effects: bool = True,
    sort_by: str = "date_modified",
    skip_seconds: float = 0
) -> str:
    """
    Generate a romantic slideshow video from images with music.

    Args:
        images_folder: Path to folder containing images
        music_track: Predefined music track ID (e.g., 'sensual_latin')
        youtube_url: YouTube URL to extract audio from
        music_file: Direct path to music file
        output_path: Custom output path
        use_effects: Enable Ken Burns and crossfade (default True)
        sort_by: How to sort images (date_modified, filename, random)
        skip_seconds: Skip first N seconds of YouTube audio (default 0)

    Returns:
        Path to the generated video
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = os.path.basename(os.path.normpath(images_folder))

    # Create working directories
    work_dir = os.path.join(TEMP_DIR, f"{folder_name}_{timestamp}")
    os.makedirs(work_dir, exist_ok=True)

    # Set output path
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, f"{folder_name}_{timestamp}.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Determine settings
    ken_burns = KEN_BURNS_ENABLED and use_effects
    crossfade = CROSSFADE_ENABLED and use_effects

    print("=" * 60)
    print("PASSPARADISE - Romantic Slideshow Generator")
    print("=" * 60)
    print(f"Images: {images_folder}")
    print(f"Output: {output_path}")
    print("-" * 60)
    print(f"Effects: Ken Burns={ken_burns}, Crossfade={crossfade}")
    print("=" * 60)

    # Step 1: Load images
    print("\n[1/4] Loading images...")
    images = load_images_from_folder(images_folder, sort_by)
    print(f"  Found {len(images)} images (sorted by {sort_by})")

    # Step 2: Get music
    print("\n[2/4] Getting music...")
    music_path = None
    attribution = ""

    if music_file and os.path.exists(music_file):
        music_path = music_file
        print(f"  Using provided file: {music_file}")
    elif youtube_url:
        print(f"  Extracting from YouTube: {youtube_url}")
        if skip_seconds > 0:
            print(f"  Skipping first {skip_seconds} seconds")
        music_path = extract_audio(youtube_url, skip_seconds=skip_seconds)
        if not music_path:
            print("  ERROR: Failed to extract audio from YouTube")
            sys.exit(1)
        print(f"  Extracted: {music_path}")
    else:
        track_id = music_track or "sensual_latin"
        print(f"  Downloading track: {track_id}")
        music_path = get_music_path(track_id)
        if not music_path:
            print(f"  ERROR: Failed to get music track: {track_id}")
            sys.exit(1)
        attribution = get_attribution(track_id)
        print(f"  Using: {music_path}")

    duration = get_audio_duration(music_path)
    print(f"  Duration: {duration:.1f}s ({duration/60:.1f} min)")

    # Step 3: Assemble video
    print("\n[3/4] Assembling video...")
    assemble_slideshow(
        images=images,
        music_path=music_path,
        output_path=output_path,
        temp_dir=work_dir,
        width=VIDEO_WIDTH,
        height=VIDEO_HEIGHT,
        ken_burns=ken_burns,
        crossfade=crossfade,
        crossfade_duration=CROSSFADE_DURATION,
        music_volume=BACKGROUND_MUSIC_VOLUME
    )

    # Step 4: Cleanup
    print("\n[4/4] Cleaning up temporary files...")
    shutil.rmtree(work_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    print("VIDEO GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Output: {output_path}")

    # Get video file size
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Size: {size_mb:.1f} MB")

    # Show features used
    features = []
    if ken_burns:
        features.append("Ken Burns")
    if crossfade:
        features.append("Crossfade")
    print(f"Features: {', '.join(features) if features else 'Basic'}")

    # Show attribution if needed
    if attribution:
        print("\n" + "-" * 60)
        print("ATTRIBUTION (add to video description):")
        print(attribution)

    print("=" * 60)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate romantic slideshow video from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/images/
  %(prog)s /path/to/images/ --music slow_burn
  %(prog)s /path/to/images/ --youtube-audio "https://youtube.com/watch?v=..."
  %(prog)s /path/to/images/ --music-file /path/to/my_song.mp3

Available music tracks:
  sensual_latin   - Latin sensual vibe (default)
  slow_burn       - Sultry, slow-building atmosphere
  evening_romance - Mysterious romantic evening
  tender_moment   - Soft, gentle romantic piano
  romantic_night  - Smooth sax for romantic nights
        """
    )
    parser.add_argument(
        "images_folder",
        help="Path to folder containing images"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output video path (default: output/<folder>_<timestamp>.mp4)"
    )
    parser.add_argument(
        "--music", "-m",
        choices=list(MUSIC_TRACKS.keys()),
        help="Predefined music track to use"
    )
    parser.add_argument(
        "--youtube-audio", "-y",
        dest="youtube_url",
        help="YouTube URL to extract audio from"
    )
    parser.add_argument(
        "--skip", "-s",
        type=float,
        default=10,
        help="Skip first N seconds of YouTube audio (default: 10)"
    )
    parser.add_argument(
        "--music-file", "-f",
        help="Direct path to music file"
    )
    parser.add_argument(
        "--sort",
        default="date_modified",
        choices=["date_modified", "filename", "random"],
        help="How to sort images (default: date_modified)"
    )
    parser.add_argument(
        "--no-effects",
        action="store_true",
        help="Disable Ken Burns and crossfade effects"
    )
    parser.add_argument(
        "--list-music",
        action="store_true",
        help="List available music tracks and exit"
    )

    args = parser.parse_args()

    if args.list_music:
        from scripts.music_downloader import list_tracks
        list_tracks()
        return

    if not os.path.isdir(args.images_folder):
        print(f"Error: Folder not found: {args.images_folder}")
        sys.exit(1)

    generate_video(
        images_folder=args.images_folder,
        music_track=args.music,
        youtube_url=args.youtube_url,
        music_file=args.music_file,
        output_path=args.output,
        use_effects=not args.no_effects,
        sort_by=args.sort,
        skip_seconds=args.skip
    )


if __name__ == "__main__":
    main()
