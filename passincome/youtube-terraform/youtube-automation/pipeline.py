#!/usr/bin/env python3
"""
YouTube Kids Stories Automation - Main Pipeline
Converts story text files into complete YouTube videos.

Features:
- Ken Burns effect (subtle zoom on images)
- Crossfade transitions between scenes
- Background music (soft 15% volume)
- Leonardo.ai AI-generated images (optional)
- Perfect A/V sync with storyline

Usage:
    python pipeline.py stories/little_star.txt
    python pipeline.py stories/little_star.txt --output my_video.mp4
    python pipeline.py stories/little_star.txt --no-music
    python pipeline.py stories/little_star.txt --no-effects
"""
import os
import sys
import argparse
import shutil
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    OUTPUT_DIR, TEMP_DIR, VIDEO_WIDTH, VIDEO_HEIGHT,
    TTS_VOICE, TTS_RATE, TTS_PITCH, INTRO_DURATION, OUTRO_DURATION,
    KEN_BURNS_ENABLED, CROSSFADE_ENABLED, CROSSFADE_DURATION,
    BACKGROUND_MUSIC_ENABLED, BACKGROUND_MUSIC_VOLUME, DEFAULT_MUSIC_FILE,
    USE_AI_IMAGES
)
from scripts.scene_parser import load_story_from_file
from scripts.tts_generator import generate_all_scenes_sync
from scripts.image_generator import generate_all_images
from scripts.video_assembler import assemble_full_video, add_background_music
from scripts.music_downloader import get_music_path
import subprocess


def combine_audio_files(audio_files: list, output_path: str) -> str:
    """Combine multiple audio files into one using FFmpeg."""
    if not audio_files:
        return None

    # Create a temp file list for ffmpeg concat
    list_file = output_path + '.txt'
    with open(list_file, 'w') as f:
        for audio in audio_files:
            f.write(f"file '{os.path.abspath(audio)}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_file,
        '-c:a', 'libmp3lame',
        '-b:a', '192k',
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception as e:
        print(f"  Warning: Could not combine audio: {e}")
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)

    return output_path


def generate_video(
    story_path: str,
    output_path: str = None,
    use_effects: bool = True,
    use_music: bool = True,
    use_ai_images: bool = None
) -> str:
    """
    Generate a complete video from a story file.

    Args:
        story_path: Path to the story text file
        output_path: Optional custom output path
        use_effects: Enable Ken Burns and crossfade (default True)
        use_music: Add background music (default True)
        use_ai_images: Use AI-generated images (default from config)

    Returns:
        Path to the generated video
    """
    story_name = os.path.splitext(os.path.basename(story_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create working directories
    work_dir = os.path.join(TEMP_DIR, f"{story_name}_{timestamp}")
    audio_dir = os.path.join(work_dir, "audio")
    image_dir = os.path.join(work_dir, "images")
    video_temp_dir = os.path.join(work_dir, "video_temp")

    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(video_temp_dir, exist_ok=True)

    # Set output path
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, f"{story_name}_{timestamp}.mp4")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Determine settings
    ken_burns = KEN_BURNS_ENABLED and use_effects
    crossfade = CROSSFADE_ENABLED and use_effects
    add_music = BACKGROUND_MUSIC_ENABLED and use_music
    ai_images = USE_AI_IMAGES if use_ai_images is None else use_ai_images

    print("=" * 60)
    print(f"YOUTUBE VIDEO GENERATOR - Enhanced")
    print("=" * 60)
    print(f"Story: {story_path}")
    print(f"Output: {output_path}")
    print("-" * 60)
    print(f"Effects: Ken Burns={ken_burns}, Crossfade={crossfade}")
    print(f"Music: {add_music}, AI Images: {ai_images}")
    print("=" * 60)

    # Step 1: Parse story
    print("\n[1/5] Parsing story...")
    story = load_story_from_file(story_path)
    title = story['title']
    scenes = story['scenes']
    print(f"  Title: {title}")
    print(f"  Scenes: {len(scenes)}")

    # Step 2: Generate TTS audio
    print("\n[2/5] Generating voice narration...")
    audio_files = generate_all_scenes_sync(
        scenes, audio_dir,
        voice=TTS_VOICE,
        rate=TTS_RATE,
        pitch=TTS_PITCH
    )
    print(f"  Generated {len(audio_files)} audio files")

    # Save combined audio separately for debugging
    combined_audio_path = os.path.join(OUTPUT_DIR, f"{story_name}_{timestamp}_audio.mp3")
    combine_audio_files(audio_files, combined_audio_path)
    print(f"  Combined audio saved to: {combined_audio_path}")

    # Step 3: Generate images (with AI if available)
    print("\n[3/5] Generating images...")
    images = generate_all_images(
        scenes, title, image_dir,
        width=VIDEO_WIDTH,
        height=VIDEO_HEIGHT,
        use_ai=ai_images
    )
    print(f"  Generated intro, {len(images['scenes'])} scenes, outro")

    # Step 4: Assemble video with effects
    print("\n[4/5] Assembling video with effects...")
    base_video = os.path.join(video_temp_dir, "base_video.mp4")

    assemble_full_video(
        intro_image=images['intro'],
        scene_images=images['scenes'],
        scene_audios=audio_files,
        outro_image=images['outro'],
        output_path=base_video,
        temp_dir=video_temp_dir,
        intro_duration=INTRO_DURATION,
        outro_duration=OUTRO_DURATION,
        width=VIDEO_WIDTH,
        height=VIDEO_HEIGHT,
        ken_burns=ken_burns,
        crossfade=crossfade,
        crossfade_duration=CROSSFADE_DURATION
    )

    # Step 5: Add background music
    if add_music:
        print("\n[5/5] Adding background music...")
        music_path = get_music_path("kids_adventure")

        if music_path and os.path.exists(music_path):
            try:
                add_background_music(
                    base_video,
                    music_path,
                    output_path,
                    music_volume=BACKGROUND_MUSIC_VOLUME
                )
                print(f"  Added music at {int(BACKGROUND_MUSIC_VOLUME * 100)}% volume")
            except Exception as e:
                print(f"  Music failed: {e}, using video without music")
                shutil.copy(base_video, output_path)
        else:
            print("  No music file found, skipping...")
            shutil.copy(base_video, output_path)
    else:
        print("\n[5/5] Skipping music (disabled)...")
        shutil.copy(base_video, output_path)

    # Cleanup temp directory
    print("\nCleaning up temporary files...")
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
    if add_music:
        features.append("Background Music")
    if ai_images:
        features.append("AI Images")
    print(f"Features: {', '.join(features) if features else 'Basic'}")
    print("=" * 60)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate YouTube video from story file with effects"
    )
    parser.add_argument(
        "story",
        help="Path to story text file"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output video path (default: output/<story_name>_<timestamp>.mp4)"
    )
    parser.add_argument(
        "--no-effects",
        action="store_true",
        help="Disable Ken Burns and crossfade effects"
    )
    parser.add_argument(
        "--no-music",
        action="store_true",
        help="Disable background music"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI image generation (use placeholders)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.story):
        print(f"Error: Story file not found: {args.story}")
        sys.exit(1)

    generate_video(
        args.story,
        args.output,
        use_effects=not args.no_effects,
        use_music=not args.no_music,
        use_ai_images=not args.no_ai if args.no_ai else None
    )


if __name__ == "__main__":
    main()
