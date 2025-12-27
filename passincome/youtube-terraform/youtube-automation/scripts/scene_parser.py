"""
Scene Parser - Extract scenes from story text files
Format: [SCENE: image description] followed by narration text
"""
import re
from typing import List, Dict


def parse_story(story_text: str) -> Dict:
    """
    Parse a story file and extract title, scenes with image prompts and narration.

    Returns:
        {
            'title': str,
            'scenes': [
                {'image_prompt': str, 'narration': str},
                ...
            ]
        }
    """
    lines = story_text.strip().split('\n')

    # Extract title (first line starting with "Title:")
    title = "Untitled Story"
    for line in lines:
        if line.lower().startswith("title:"):
            title = line.split(":", 1)[1].strip()
            break

    # Extract scenes using regex
    # Pattern: [SCENE: description] followed by text until next [SCENE:] or end
    pattern = r'\[SCENE:\s*([^\]]+)\]\s*'

    # Split by scene markers
    parts = re.split(pattern, story_text)

    scenes = []
    # parts[0] is text before first scene (title, etc.)
    # parts[1], parts[2] = first scene prompt, first scene narration
    # parts[3], parts[4] = second scene prompt, second scene narration, etc.

    for i in range(1, len(parts) - 1, 2):
        image_prompt = parts[i].strip()
        narration = parts[i + 1].strip() if i + 1 < len(parts) else ""

        # Clean up narration - remove any trailing scene markers that got included
        narration = re.split(r'\[SCENE:', narration)[0].strip()

        if image_prompt and narration:
            scenes.append({
                'image_prompt': image_prompt,
                'narration': narration
            })

    return {
        'title': title,
        'scenes': scenes
    }


def load_story_from_file(filepath: str) -> Dict:
    """Load and parse a story from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_story(content)


def get_scene_duration(narration: str, words_per_second: float = 2.5, min_duration: float = 4.0) -> float:
    """
    Calculate scene duration based on narration length.

    Args:
        narration: The narration text
        words_per_second: Reading speed
        min_duration: Minimum duration in seconds

    Returns:
        Duration in seconds
    """
    word_count = len(narration.split())
    calculated_duration = word_count / words_per_second
    return max(calculated_duration, min_duration)


if __name__ == "__main__":
    # Test with sample story
    sample = """
Title: The Little Star Who Found a Friend

[SCENE: A dark night sky filled with twinkling stars of all sizes]
High up in the velvet night sky, thousands of stars twinkled and danced.

[SCENE: A tiny star with a sad face, smaller than all other stars around it]
Among them was Twinkle, the tiniest star of all. She often felt lonely because the other stars seemed so far away.

[SCENE: A little girl with pigtails looking out her bedroom window at the stars]
Down on Earth, a little girl named Maya loved to watch the stars from her window every night.
"""

    result = parse_story(sample)
    print(f"Title: {result['title']}")
    print(f"Number of scenes: {len(result['scenes'])}")
    for i, scene in enumerate(result['scenes'], 1):
        duration = get_scene_duration(scene['narration'])
        print(f"\nScene {i} ({duration:.1f}s):")
        print(f"  Image: {scene['image_prompt'][:50]}...")
        print(f"  Narration: {scene['narration'][:50]}...")
