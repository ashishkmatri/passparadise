#!/usr/bin/env python3
"""
Music Video Creator - Creates slideshow videos from images with audio
Usage: python create_music_video.py --images /path/to/images --audio /path/to/audio.mp3 --duration 7
"""

import argparse
import os
import subprocess
import random
import sys
import tempfile
from pathlib import Path


def get_images(image_path: str) -> list:
    """Get all image files from path (supports jpg, jpeg, png)"""
    path = Path(image_path)
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    images = []
    for ext in extensions:
        images.extend(path.glob(ext))
    return sorted(images)


def shuffle_images(images: list) -> list:
    """Shuffle images - if from multiple folders, avoid same folder back-to-back"""
    # Group by parent folder
    folders = {}
    for img in images:
        folder = img.parent.name
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(img)

    # If all from same folder, just shuffle
    if len(folders) == 1:
        shuffled = list(images)
        random.shuffle(shuffled)
        return shuffled

    # Shuffle within each folder
    for folder in folders:
        random.shuffle(folders[folder])

    # Interleave - round-robin
    result = []
    folder_names = list(folders.keys())
    random.shuffle(folder_names)

    while any(folders[f] for f in folder_names):
        for fname in folder_names:
            if folders[fname]:
                result.append(folders[fname].pop(0))

    # Fix back-to-back from same folder
    for i in range(1, len(result)):
        if result[i].parent.name == result[i-1].parent.name:
            for j in range(i+1, len(result)):
                if result[j].parent.name != result[i].parent.name:
                    result[i], result[j] = result[j], result[i]
                    break

    return result


def create_concat_file(images: list, duration: int, output_file: str) -> None:
    """Create FFmpeg concat file"""
    with open(output_file, 'w') as f:
        for img in images:
            # Escape single quotes in path
            img_path = str(img).replace("'", "'\\''")
            f.write(f"file '{img_path}'\n")
            f.write(f"duration {duration}\n")
        # Add last image without duration (required by concat)
        last_path = str(images[-1]).replace("'", "'\\''")
        f.write(f"file '{last_path}'\n")


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds"""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        import json
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    return 0


def create_video(concat_file: str, audio_path: str, output_path: str,
                 total_duration: int, resolution: str = "1920:1080") -> bool:
    """Create video using FFmpeg"""
    width, height = resolution.split(':')

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-i', audio_path,
        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '192k',
        '-t', str(total_duration),
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_path
    ]

    print(f"Running FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr[-500:]}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description='Create music video from images')
    parser.add_argument('--images', '-i', required=True, help='Path to images folder')
    parser.add_argument('--audio', '-a', required=True, help='Path to audio file (mp3, m4a, etc)')
    parser.add_argument('--duration', '-d', type=int, default=7, help='Duration per image in seconds (default: 7)')
    parser.add_argument('--output', '-o', default='output_video.mp4', help='Output video path (default: output_video.mp4)')
    parser.add_argument('--resolution', '-r', default='1920:1080', help='Video resolution (default: 1920:1080)')
    parser.add_argument('--no-shuffle', action='store_true', help='Disable image shuffling')

    args = parser.parse_args()

    # Validate inputs
    if not os.path.isdir(args.images):
        print(f"Error: Images path not found: {args.images}")
        sys.exit(1)

    if not os.path.isfile(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        sys.exit(1)

    # Get images
    images = get_images(args.images)
    if not images:
        print(f"Error: No images found in {args.images}")
        sys.exit(1)

    print(f"Found {len(images)} images")

    # Shuffle images
    if args.no_shuffle:
        ordered_images = images
    else:
        ordered_images = shuffle_images(images)
        print("Images shuffled (no same folder back-to-back)")

    # Calculate total duration
    total_duration = len(ordered_images) * args.duration
    print(f"Video duration: {total_duration} seconds ({total_duration // 60}m {total_duration % 60}s)")
    print(f"Each image: {args.duration} seconds")

    # Create concat file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        concat_file = f.name

    create_concat_file(ordered_images, args.duration, concat_file)

    # Create video
    print(f"Creating video: {args.output}")
    success = create_video(concat_file, args.audio, args.output, total_duration, args.resolution)

    # Cleanup
    os.unlink(concat_file)

    if success:
        size = os.path.getsize(args.output) / (1024 * 1024)
        print(f"\nSuccess! Video created: {args.output}")
        print(f"Size: {size:.1f} MB")
        print(f"Duration: {total_duration // 60}m {total_duration % 60}s")
    else:
        print("Failed to create video")
        sys.exit(1)


if __name__ == '__main__':
    main()
