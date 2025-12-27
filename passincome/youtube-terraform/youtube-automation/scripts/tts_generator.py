"""
TTS Generator - Generate voice narration using edge-tts (FREE Microsoft neural voices)

Best voices for kids storytelling (clear and expressive):
- en-US-JennyNeural: Clear, friendly female voice (RECOMMENDED)
- en-US-AriaNeural: Expressive, warm female voice
- en-US-SaraNeural: Natural, conversational female voice
- en-GB-SoniaNeural: British, clear female voice
"""
import asyncio
import os
import edge_tts
from typing import List, Optional


async def generate_voice(
    text: str,
    output_path: str,
    voice: str = "en-US-JennyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> str:
    """
    Generate TTS audio using edge-tts.

    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        voice: Voice to use (default: en-US-JennyNeural - clear, friendly)
        rate: Speech rate adjustment (default: normal speed)
        pitch: Pitch adjustment (default: normal)

    Returns:
        Path to the generated audio file
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)
    return output_path


async def generate_scene_audio(
    scenes: List[dict],
    output_dir: str,
    voice: str = "en-US-JennyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> List[str]:
    """
    Generate audio files for all scenes.

    Args:
        scenes: List of scene dicts with 'narration' key
        output_dir: Directory to save audio files
        voice: Voice to use
        rate: Speech rate
        pitch: Pitch adjustment

    Returns:
        List of paths to generated audio files
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_files = []

    for i, scene in enumerate(scenes):
        output_path = os.path.join(output_dir, f"scene_{i:02d}.mp3")
        await generate_voice(scene['narration'], output_path, voice, rate, pitch)
        audio_files.append(output_path)
        print(f"Generated audio for scene {i + 1}/{len(scenes)}")

    return audio_files


def generate_audio_sync(
    text: str,
    output_path: str,
    voice: str = "en-US-JennyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> str:
    """Synchronous wrapper for generate_voice."""
    return asyncio.run(generate_voice(text, output_path, voice, rate, pitch))


def generate_all_scenes_sync(
    scenes: List[dict],
    output_dir: str,
    voice: str = "en-US-JennyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> List[str]:
    """Synchronous wrapper for generate_scene_audio."""
    return asyncio.run(generate_scene_audio(scenes, output_dir, voice, rate, pitch))


async def list_voices(language: str = "en") -> List[dict]:
    """List available voices for a language."""
    voices = await edge_tts.list_voices()
    return [v for v in voices if v['Locale'].startswith(language)]


if __name__ == "__main__":
    # Test TTS generation
    import sys

    test_text = "Hello little friends! Welcome to story time. Tonight, we have a magical tale just for you."
    output_file = "test_audio.mp3"

    print(f"Generating test audio: {test_text[:50]}...")
    result = generate_audio_sync(test_text, output_file)
    print(f"Audio saved to: {result}")

    # List some available voices
    print("\nAvailable English voices:")
    voices = asyncio.run(list_voices("en"))
    for v in voices[:10]:
        print(f"  {v['ShortName']}: {v['Gender']}")
