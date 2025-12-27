#!/usr/bin/env python3
"""
FULLY AUTOMATED YouTube Video Generator

Generates complete YouTube kids story videos with ONE command.
Story is optional - if not provided, generates a random story.

Usage:
    python generate.py                           # Fully random story + video
    python generate.py --theme friendship        # Random story with theme
    python generate.py --character penguin       # Random story with character
    python generate.py --story stories/my.txt    # Use existing story file
    python generate.py --batch 5                 # Generate 5 random videos

Examples:
    python generate.py                           # Quick random video
    python generate.py --theme courage --character rabbit
    python generate.py --batch 10 --theme friendship
"""
import os
import sys
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import STORIES_DIR, OUTPUT_DIR
from scripts.story_generator import generate_story_from_template, save_story, THEMES, CHARACTERS
from pipeline import generate_video


def generate_full_video(
    story_path: str = None,
    theme: str = None,
    character: str = None,
    output_path: str = None
) -> str:
    """
    Generate a complete video - story optional.

    If no story_path provided, generates a random story first.
    """

    # Step 0: Generate story if not provided
    if story_path is None:
        print("\n" + "=" * 60)
        print("STEP 0: Generating Story...")
        print("=" * 60)

        # Find character tuple if specified
        char_tuple = None
        if character:
            for c in CHARACTERS:
                if character.lower() in c[0].lower():
                    char_tuple = c
                    break

        # Generate story
        story_text = generate_story_from_template(theme=theme, character=char_tuple)

        # Save story
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        story_filename = f"auto_generated_{timestamp}.txt"
        story_path = save_story(story_text, story_filename, STORIES_DIR)

        print(f"  Generated story: {story_path}")

        # Show title
        title_line = story_text.split('\n')[0]
        print(f"  {title_line}")

    # Generate video from story
    return generate_video(story_path, output_path)


def batch_generate(count: int, theme: str = None):
    """Generate multiple random videos."""
    print(f"\n{'=' * 60}")
    print(f"BATCH GENERATION: {count} videos")
    print(f"{'=' * 60}")

    results = []
    for i in range(count):
        print(f"\n[{i+1}/{count}] Generating video...")
        try:
            output = generate_full_video(theme=theme)
            results.append(("SUCCESS", output))
        except Exception as e:
            print(f"ERROR: {e}")
            results.append(("FAILED", str(e)))

    # Summary
    print(f"\n{'=' * 60}")
    print("BATCH COMPLETE")
    print(f"{'=' * 60}")
    success = sum(1 for r in results if r[0] == "SUCCESS")
    print(f"Successful: {success}/{count}")

    for i, (status, path) in enumerate(results, 1):
        print(f"  [{status}] Video {i}: {path if status == 'SUCCESS' else 'Failed'}")


def main():
    parser = argparse.ArgumentParser(
        description="Fully automated YouTube video generator"
    )
    parser.add_argument(
        "--story", "-s",
        help="Path to existing story file (optional - generates random if not provided)"
    )
    parser.add_argument(
        "--theme", "-t",
        choices=list(THEMES.keys()),
        help="Story theme for auto-generation"
    )
    parser.add_argument(
        "--character", "-c",
        help="Character type (penguin, rabbit, owl, etc.)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output video path"
    )
    parser.add_argument(
        "--batch", "-b",
        type=int,
        help="Generate multiple random videos"
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes"
    )
    parser.add_argument(
        "--list-characters",
        action="store_true",
        help="List available characters"
    )

    args = parser.parse_args()

    if args.list_themes:
        print("\nAvailable Themes:")
        for theme, data in THEMES.items():
            print(f"  {theme}: {data['moral']}")
        return

    if args.list_characters:
        print("\nAvailable Characters:")
        for char_type, name, setting in CHARACTERS:
            print(f"  {char_type}: {name} (in {setting})")
        return

    if args.batch:
        batch_generate(args.batch, args.theme)
    else:
        generate_full_video(
            story_path=args.story,
            theme=args.theme,
            character=args.character,
            output_path=args.output
        )


if __name__ == "__main__":
    main()
