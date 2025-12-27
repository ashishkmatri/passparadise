"""
Video Assembler - Combine images and audio into final video using FFmpeg

Features:
- Perfect A/V sync (audio-driven timing)
- Crossfade transitions between scenes
- Ken Burns effect (subtle pan/zoom)
- Background music support (soft 15% volume)
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
    duration = float(data['format']['duration'])

    # Debug: print audio info
    if 'streams' in data:
        for stream in data['streams']:
            if stream.get('codec_type') == 'audio':
                sample_rate = stream.get('sample_rate', 'unknown')
                print(f"    Audio: {sample_rate}Hz, duration={duration:.2f}s")

    return duration


def get_video_duration(video_path: str) -> float:
    """Get duration of video file in seconds."""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def create_scene_video_with_effects(
    image_path: str,
    audio_path: str,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    ken_burns: bool = True
) -> str:
    """
    Create video clip with Ken Burns effect (subtle zoom).

    Two-step process to avoid audio timing issues:
    1. Create silent video from image
    2. Overlay audio using -shortest to match durations
    """
    duration = get_audio_duration(audio_path)
    fps = 25
    total_frames = int(duration * fps) + 1

    # Step 1: Create silent video
    silent_video = output_path + '.silent.mp4'

    if ken_burns and total_frames > 0:
        zoom_increment = 0.04 / total_frames

        filter_complex = (
            f"scale=2112:1188,setsar=1,"
            f"zoompan=z='1+{zoom_increment}*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={total_frames}:s={width}x{height}:fps={fps}"
        )

        cmd_video = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration + 0.5),  # Slightly longer to ensure coverage
            '-an',  # No audio
            silent_video
        ]
    else:
        cmd_video = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration + 0.5),
            '-an',
            silent_video
        ]

    subprocess.run(cmd_video, check=True, capture_output=True)

    # Step 2: Overlay audio onto silent video
    # CRITICAL: Use -async 1 to sync audio/video timestamps properly
    # and keep original audio sample rate to avoid speed issues
    cmd_audio = [
        'ffmpeg', '-y',
        '-i', silent_video,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-async', '1',  # Sync audio to video timestamps
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_path
    ]

    result = subprocess.run(cmd_audio, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    FFmpeg audio overlay error: {result.stderr[:200]}")

    # Cleanup
    if os.path.exists(silent_video):
        os.remove(silent_video)

    return output_path


def create_scene_video(
    image_path: str,
    audio_path: str,
    output_path: str,
    width: int = 1920,
    height: int = 1080
) -> str:
    """Create a simple video clip (fallback without effects).

    Two-step process to avoid audio timing issues:
    1. Create silent video from image
    2. Overlay audio
    """
    duration = get_audio_duration(audio_path)
    fps = 25

    # Step 1: Create silent video
    silent_video = output_path + '.silent.mp4'
    cmd_video = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', image_path,
        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-pix_fmt', 'yuv420p',
        '-t', str(duration + 0.5),
        '-an',
        silent_video
    ]

    subprocess.run(cmd_video, check=True, capture_output=True)

    # Step 2: Overlay audio with proper sync
    cmd_audio = [
        'ffmpeg', '-y',
        '-i', silent_video,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-async', '1',  # Sync audio to video timestamps
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_path
    ]

    result = subprocess.run(cmd_audio, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    FFmpeg audio overlay error: {result.stderr[:200]}")

    # Cleanup
    if os.path.exists(silent_video):
        os.remove(silent_video)

    return output_path


def create_silent_clip(
    image_path: str,
    duration: float,
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    ken_burns: bool = True,
    fade_out: bool = False
) -> str:
    """Create silent video clip from image (for intro/outro)."""
    fps = 25
    total_frames = int(duration * fps)

    filters = []

    if ken_burns and total_frames > 0:
        zoom_increment = 0.04 / total_frames
        filters.append(f"scale=2112:1188,setsar=1")
        filters.append(
            f"zoompan=z='1+{zoom_increment}*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={total_frames}:s={width}x{height}:fps={fps}"
        )
    else:
        filters.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease")
        filters.append(f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2")

    # Add fade out for outro
    if fade_out:
        filters.append(f"fade=t=out:st={duration-1}:d=1")

    filter_str = ','.join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', image_path,
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-vf', filter_str,
        '-c:v', 'libx264',
        '-preset', 'medium',
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
    crossfade_duration: float = 0.3
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
    """Simple concatenation without effects.

    Uses stream copy for both video and audio since all clips are
    already encoded with consistent settings (aac, 44100Hz).
    """
    list_file = output_path + '.txt'
    with open(list_file, 'w') as f:
        for video in video_files:
            f.write(f"file '{os.path.abspath(video)}'\n")

    # Use copy for both streams - clips already have consistent encoding
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


def assemble_full_video(
    intro_image: str,
    scene_images: List[str],
    scene_audios: List[str],
    outro_image: str,
    output_path: str,
    temp_dir: str,
    intro_duration: float = 3.0,
    outro_duration: float = 4.0,
    width: int = 1920,
    height: int = 1080,
    ken_burns: bool = True,
    crossfade: bool = True,
    crossfade_duration: float = 0.3
) -> str:
    """
    Assemble complete video with all effects.

    Features:
    - Ken Burns effect (subtle zoom on each scene)
    - Crossfade transitions between scenes
    - Perfect A/V sync
    """
    os.makedirs(temp_dir, exist_ok=True)
    video_clips = []

    print("Creating intro clip...")
    intro_clip = os.path.join(temp_dir, "intro.mp4")
    create_silent_clip(intro_image, intro_duration, intro_clip, width, height, ken_burns=ken_burns)
    video_clips.append(intro_clip)

    print(f"Creating {len(scene_images)} scene clips with effects...")
    for i, (image, audio) in enumerate(zip(scene_images, scene_audios)):
        scene_clip = os.path.join(temp_dir, f"scene_{i:02d}.mp4")

        try:
            create_scene_video_with_effects(image, audio, scene_clip, width, height, ken_burns=ken_burns)
        except Exception as e:
            print(f"  Effects failed for scene {i+1}, using simple: {e}")
            create_scene_video(image, audio, scene_clip, width, height)

        video_clips.append(scene_clip)
        print(f"  Scene {i + 1}/{len(scene_images)} complete")

    print("Creating outro clip...")
    outro_clip = os.path.join(temp_dir, "outro.mp4")
    create_silent_clip(outro_image, outro_duration, outro_clip, width, height, ken_burns=ken_burns, fade_out=True)
    video_clips.append(outro_clip)

    print("Concatenating all clips...")
    if crossfade and len(video_clips) > 1:
        try:
            concatenate_with_crossfade(video_clips, output_path, crossfade_duration)
        except Exception as e:
            print(f"  Crossfade failed: {e}")
            concatenate_videos(video_clips, output_path)
    else:
        concatenate_videos(video_clips, output_path)

    # Clean up temp clips
    for clip in video_clips:
        if os.path.exists(clip):
            os.remove(clip)

    print(f"Video saved to: {output_path}")
    return output_path


def add_background_music(
    video_path: str,
    music_path: str,
    output_path: str,
    music_volume: float = 0.15
) -> str:
    """
    Add soft background music to video (15% volume by default).

    Music fades in at start and fades out at end.
    """
    duration = get_video_duration(video_path)
    fade_out_start = max(0, duration - 3)

    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-stream_loop', '-1',
        '-i', music_path,
        '-filter_complex',
        f'[1:a]volume={music_volume},afade=t=in:d=2,afade=t=out:st={fade_out_start}:d=3[music];'
        f'[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[out]',
        '-map', '0:v',
        '-map', '[out]',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_path
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


if __name__ == "__main__":
    print("Video Assembler - Enhanced")
    print("Features:")
    print("  - Ken Burns effect (subtle zoom)")
    print("  - Crossfade transitions")
    print("  - Background music (15% volume)")
    print("  - Perfect A/V sync")
