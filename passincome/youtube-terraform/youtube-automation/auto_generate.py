#!/usr/bin/env python3
"""
Auto Generate - One-command video generation for all stories
Batch process multiple story files or generate a single video.

Usage:
    python auto_generate.py                    # Generate all stories
    python auto_generate.py --story little_star  # Generate specific story
    python auto_generate.py --list             # List available stories
"""
import os
import sys
import argparse
import glob
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import STORIES_DIR, OUTPUT_DIR
from pipeline import generate_video


def list_stories():
    """List all available story files."""
    stories = glob.glob(os.path.join(STORIES_DIR, "*.txt"))
    if not stories:
        print("No stories found in:", STORIES_DIR)
        return []

    print("\nAvailable Stories:")
    print("-" * 40)
    for story in sorted(stories):
        name = os.path.splitext(os.path.basename(story))[0]
        print(f"  - {name}")
    print("-" * 40)
    print(f"Total: {len(stories)} stories")
    return stories


def generate_all():
    """Generate videos for all stories."""
    stories = glob.glob(os.path.join(STORIES_DIR, "*.txt"))

    if not stories:
        print("No stories found in:", STORIES_DIR)
        return

    print(f"\nGenerating videos for {len(stories)} stories...")
    print("=" * 60)

    results = []
    for i, story_path in enumerate(sorted(stories), 1):
        story_name = os.path.splitext(os.path.basename(story_path))[0]
        print(f"\n[{i}/{len(stories)}] Processing: {story_name}")

        try:
            output = generate_video(story_path)
            results.append((story_name, "SUCCESS", output))
        except Exception as e:
            print(f"ERROR: {e}")
            results.append((story_name, "FAILED", str(e)))

    # Summary
    print("\n" + "=" * 60)
    print("BATCH GENERATION SUMMARY")
    print("=" * 60)
    success = sum(1 for r in results if r[1] == "SUCCESS")
    print(f"Successful: {success}/{len(results)}")
    print("\nResults:")
    for name, status, output in results:
        print(f"  [{status}] {name}")
        if status == "SUCCESS":
            print(f"           -> {output}")


def generate_single(story_name: str):
    """Generate video for a single story by name."""
    # Try exact match first
    story_path = os.path.join(STORIES_DIR, f"{story_name}.txt")

    if not os.path.exists(story_path):
        # Try partial match
        stories = glob.glob(os.path.join(STORIES_DIR, f"*{story_name}*.txt"))
        if len(stories) == 1:
            story_path = stories[0]
        elif len(stories) > 1:
            print(f"Multiple matches for '{story_name}':")
            for s in stories:
                print(f"  - {os.path.basename(s)}")
            return
        else:
            print(f"Story not found: {story_name}")
            list_stories()
            return

    generate_video(story_path)


def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate YouTube videos from stories"
    )
    parser.add_argument(
        "--story", "-s",
        help="Generate specific story by name"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available stories"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate all stories"
    )

    args = parser.parse_args()

    if args.list:
        list_stories()
    elif args.story:
        generate_single(args.story)
    elif args.all:
        generate_all()
    else:
        # Default: show help and list stories
        parser.print_help()
        print()
        list_stories()


if __name__ == "__main__":
    main()
