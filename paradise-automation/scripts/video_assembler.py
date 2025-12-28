"""
Video Assembler - Combine images and audio into final video using FFmpeg

Features:
- Ken Burns effect (subtle pan/zoom)
- Crossfade transitions between images
- Background music (full volume)
"""
import os
import subprocess
import json
from typing import List


def get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def get_video_duration(video_path: str) -> float:
    """Get duration of video file in seconds."""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def create_image_clip(
    image_path: str,
    duration: float,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    ken_burns: bool = True
) -> str:
    """
    Create video clip from a single image with Ken Burns effect.
    """
    fps = 25
    total_frames = int(duration * fps)

    if ken_burns and total_frames > 0:
        # Ken Burns: 4% zoom over duration
        zoom_increment = 0.04 / total_frames

        filter_complex = (
            f"scale=2112:1188,setsar=1,"
            f"zoompan=z='1+{zoom_increment}*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={total_frames}:s={width}x{height}:fps={fps}"
        )

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-f', 'lavfi',
            '-i', 'anullsrc=r=44100:cl=stereo',
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            output_path
        ]
    else:
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-f', 'lavfi',
            '-i', 'anullsrc=r=44100:cl=stereo',
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            output_path
        ]

    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def concatenate_with_crossfade(
    video_files: List[str],
    output_path: str,
    crossfade_duration: float = 0.5
) -> str:
    """Concatenate videos with crossfade transitions between them."""

    if len(video_files) < 2:
        if video_files:
            import shutil
            shutil.copy(video_files[0], output_path)
        return output_path

    # Build xfade filter chain
    n = len(video_files)
    inputs = []
    for f in video_files:
        inputs.extend(['-i', f])

    # Get durations
    durations = [get_video_duration(f) for f in video_files]

    # Build filter: chain of xfade filters
    filter_parts = []
    offset = durations[0] - crossfade_duration

    # First xfade
    filter_parts.append(
        f"[0:v][1:v]xfade=transition=fade:duration={crossfade_duration}:offset={offset}[v1];"
        f"[0:a][1:a]acrossfade=d={crossfade_duration}[a1]"
    )

    # Chain remaining xfades
    for i in range(2, n):
        offset += durations[i-1] - crossfade_duration
        prev_v = f"v{i-1}"
        prev_a = f"a{i-1}"
        out_v = f"v{i}"
        out_a = f"a{i}"

        filter_parts.append(
            f"[{prev_v}][{i}:v]xfade=transition=fade:duration={crossfade_duration}:offset={offset}[{out_v}];"
            f"[{prev_a}][{i}:a]acrossfade=d={crossfade_duration}[{out_a}]"
        )

    filter_str = ';'.join(filter_parts)
    final_v = f"v{n-1}"
    final_a = f"a{n-1}"

    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', filter_str,
        '-map', f'[{final_v}]',
        '-map', f'[{final_a}]',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-c:a', 'aac',
        '-b:a', '128k',
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"  Crossfade failed, using simple concat: {e}")
        concatenate_videos(video_files, output_path)

    return output_path


def concatenate_videos(video_files: List[str], output_path: str) -> str:
    """Simple concatenation without effects."""
    list_file = output_path + '.txt'
    with open(list_file, 'w') as f:
        for video in video_files:
            f.write(f"file '{os.path.abspath(video)}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_file,
        '-c', 'copy',
        output_path
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(list_file)
    return output_path


def add_background_music(
    video_path: str,
    music_path: str,
    output_path: str,
    music_volume: float = 1.0
) -> str:
    """
    Replace video audio with background music.
    Music is looped if shorter than video.
    Fades in at start and out at end.
    """
    duration = get_video_duration(video_path)
    fade_out_start = max(0, duration - 3)

    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-stream_loop', '-1',
        '-i', music_path,
        '-filter_complex',
        f'[1:a]volume={music_volume},afade=t=in:d=2,afade=t=out:st={fade_out_start}:d=3[music]',
        '-map', '0:v',
        '-map', '[music]',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_path
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def assemble_slideshow(
    images: List[str],
    music_path: str,
    output_path: str,
    temp_dir: str,
    width: int = 1920,
    height: int = 1080,
    ken_burns: bool = True,
    crossfade: bool = True,
    crossfade_duration: float = 0.5,
    music_volume: float = 1.0
) -> str:
    """
    Assemble complete slideshow video from images with music.

    Duration per image is calculated from music duration / number of images.
    """
    os.makedirs(temp_dir, exist_ok=True)

    # Get music duration
    music_duration = get_audio_duration(music_path)

    # Calculate duration per image (accounting for crossfades)
    num_images = len(images)
    if crossfade and num_images > 1:
        # Crossfades reduce total duration
        total_crossfade_time = crossfade_duration * (num_images - 1)
        available_duration = music_duration + total_crossfade_time
    else:
        available_duration = music_duration

    duration_per_image = available_duration / num_images

    # Clamp to min/max
    from config import MIN_IMAGE_DURATION, MAX_IMAGE_DURATION
    duration_per_image = max(MIN_IMAGE_DURATION, min(MAX_IMAGE_DURATION, duration_per_image))

    print(f"Music duration: {music_duration:.1f}s")
    print(f"Images: {num_images}")
    print(f"Duration per image: {duration_per_image:.1f}s")

    # Create individual clips
    video_clips = []
    for i, image in enumerate(images):
        clip_path = os.path.join(temp_dir, f"clip_{i:03d}.mp4")
        print(f"  Creating clip {i+1}/{num_images}...")
        create_image_clip(image, duration_per_image, clip_path, width, height, ken_burns)
        video_clips.append(clip_path)

    # Concatenate clips
    print("Concatenating clips...")
    silent_video = os.path.join(temp_dir, "silent_video.mp4")
    if crossfade and len(video_clips) > 1:
        try:
            concatenate_with_crossfade(video_clips, silent_video, crossfade_duration)
        except Exception as e:
            print(f"  Crossfade failed: {e}")
            concatenate_videos(video_clips, silent_video)
    else:
        concatenate_videos(video_clips, silent_video)

    # Add music
    print("Adding music...")
    add_background_music(silent_video, music_path, output_path, music_volume)

    # Cleanup
    for clip in video_clips:
        if os.path.exists(clip):
            os.remove(clip)
    if os.path.exists(silent_video):
        os.remove(silent_video)

    print(f"Video saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    print("Video Assembler - PassParadise")
    print("Features:")
    print("  - Ken Burns effect (subtle zoom)")
    print("  - Crossfade transitions")
    print("  - Background music (full volume)")
