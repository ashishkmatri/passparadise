#!/usr/bin/env python3
"""
Story Generator - Generate kids stories from simple prompts
Uses free AI APIs or local templates to create stories with [SCENE:] markers.

Usage:
    python story_generator.py "a shy penguin who makes friends"
    python story_generator.py "a brave little rabbit" --theme courage
    python story_generator.py --random  # Generate random story
"""
import os
import sys
import json
import random
import argparse
import requests
from datetime import datetime

# Story templates for offline generation
THEMES = {
    "friendship": {
        "moral": "True friends accept you for who you are",
        "emotions": ["lonely", "hopeful", "happy", "grateful"]
    },
    "courage": {
        "moral": "Being brave means doing what's right even when you're scared",
        "emotions": ["scared", "determined", "proud", "confident"]
    },
    "kindness": {
        "moral": "Small acts of kindness make the world brighter",
        "emotions": ["caring", "helpful", "joyful", "loved"]
    },
    "perseverance": {
        "moral": "Never give up, and you can achieve anything",
        "emotions": ["frustrated", "determined", "trying", "successful"]
    },
    "being_different": {
        "moral": "What makes you different makes you special",
        "emotions": ["sad", "confused", "accepting", "proud"]
    },
    "overcoming_fear": {
        "moral": "Facing our fears helps us grow stronger",
        "emotions": ["afraid", "nervous", "brave", "triumphant"]
    }
}

CHARACTERS = [
    ("star", "Twinkle", "night sky"),
    ("rabbit", "Rosie", "meadow"),
    ("penguin", "Penny", "snowy Antarctica"),
    ("owl", "Oliver", "forest"),
    ("turtle", "Tilly", "pond"),
    ("zebra", "Ziggy", "African savanna"),
    ("butterfly", "Bella", "flower garden"),
    ("bear", "Bruno", "cozy cave"),
    ("dolphin", "Danny", "ocean"),
    ("fox", "Finn", "autumn forest"),
    ("kitten", "Katie", "warm house"),
    ("elephant", "Ellie", "jungle"),
]

STORY_TEMPLATE = """Title: {title}

[SCENE: {setting} with {character_name} the {character_type} looking {emotion1}]
In the {setting}, there lived a little {character_type} named {character_name}. {character_name} was feeling {emotion1} because {problem}.

[SCENE: {character_name} looking around, noticing something that catches their attention]
One day, {character_name} noticed something unusual. {discovery}

[SCENE: {character_name} meeting {helper_name} the {helper_type}, who looks friendly]
That's when {character_name} met {helper_name} the {helper_type}. "{greeting}" said {helper_name} with a warm smile.

[SCENE: {character_name} and {helper_name} talking, {character_name} looking {emotion2}]
{character_name} explained the problem. {helper_name} listened carefully and said, "{advice}"

[SCENE: {character_name} trying something new, looking {emotion3}]
With {helper_name}'s encouragement, {character_name} decided to try. {first_attempt}

[SCENE: {character_name} facing a small challenge, but not giving up]
It wasn't easy at first. {challenge} But {character_name} remembered {helper_name}'s words and kept going.

[SCENE: {character_name} starting to succeed, a smile forming on their face]
Slowly, something wonderful began to happen. {progress}

[SCENE: {character_name} achieving the goal, looking {emotion4} and proud]
Finally, {character_name} did it! {success} {character_name} felt so {emotion4}!

[SCENE: {character_name} and {helper_name} celebrating together]
{helper_name} cheered, "I knew you could do it, {character_name}!" They celebrated together, {celebration}.

[SCENE: {character_name} helping another little {character_type} who has the same problem]
Later, {character_name} saw another little one with the same problem. Now it was {character_name}'s turn to help!

[SCENE: {character_name} sharing wisdom, looking kind and wise]
"{encouragement}" {character_name} said gently, just like {helper_name} had done.

[SCENE: {setting} at sunset, {character_name} happy and content with new friends around]
The end. Remember, {moral}
"""


def generate_story_from_template(
    prompt: str = None,
    theme: str = None,
    character: tuple = None
) -> str:
    """Generate a story using templates (offline, free)."""

    # Pick random elements if not specified
    if theme is None:
        theme = random.choice(list(THEMES.keys()))

    if character is None:
        character = random.choice(CHARACTERS)

    theme_data = THEMES.get(theme, THEMES["friendship"])
    char_type, char_name, setting = character

    # Pick a helper character (different from main)
    helper = random.choice([c for c in CHARACTERS if c[0] != char_type])
    helper_type, helper_name, _ = helper

    # Generate story elements based on theme
    story_elements = generate_story_elements(theme, char_type, char_name, setting)

    # Fill template
    story = STORY_TEMPLATE.format(
        title=f"{char_name} the {char_type.title()} Learns About {theme.replace('_', ' ').title()}",
        setting=setting,
        character_name=char_name,
        character_type=char_type,
        helper_name=helper_name,
        helper_type=helper_type,
        emotion1=theme_data["emotions"][0],
        emotion2=theme_data["emotions"][1],
        emotion3=theme_data["emotions"][2],
        emotion4=theme_data["emotions"][3],
        moral=theme_data["moral"],
        **story_elements
    )

    return story


def generate_story_elements(theme: str, char_type: str, char_name: str, setting: str) -> dict:
    """Generate story-specific elements based on theme."""

    elements = {
        "friendship": {
            "problem": f"{char_name} didn't have any friends to play with",
            "discovery": f"A new {random.choice(['butterfly', 'bird', 'creature'])} had arrived in the {setting}!",
            "greeting": "Hello there! You look like you could use a friend",
            "advice": "Making friends is easy - just be yourself and show kindness",
            "first_attempt": f"{char_name} took a deep breath and said hello to someone new.",
            "challenge": "The other animals seemed busy with their own games.",
            "progress": f"One by one, others started smiling at {char_name}.",
            "success": f"{char_name} had made not one, but many new friends!",
            "celebration": "laughing and playing together",
            "encouragement": "Don't be shy - everyone needs a friend like you",
        },
        "courage": {
            "problem": f"{char_name} was afraid of trying new things",
            "discovery": "Someone needed help, but it meant facing a scary challenge!",
            "greeting": "You look worried. What's troubling you, little one",
            "advice": "Being brave doesn't mean not being scared. It means trying anyway",
            "first_attempt": f"Though trembling a little, {char_name} took the first step.",
            "challenge": "The path seemed long and the goal seemed far away.",
            "progress": f"With each step, {char_name} felt a little braver.",
            "success": f"{char_name} conquered the fear and helped save the day!",
            "celebration": "jumping up and down with joy",
            "encouragement": "You're braver than you know. Just take one small step",
        },
        "kindness": {
            "problem": f"{char_name} saw others being unkind and felt sad",
            "discovery": "A small creature was crying and needed help.",
            "greeting": "That was very kind of you to stop and care",
            "advice": "Kindness is like magic - the more you give, the more comes back",
            "first_attempt": f"{char_name} shared some food with the hungry little one.",
            "challenge": "Some others laughed and said it was a waste of time.",
            "progress": f"But the little creature's smile made {char_name} feel warm inside.",
            "success": f"Soon, everyone wanted to be kind too, inspired by {char_name}!",
            "celebration": "sharing treats and making everyone smile",
            "encouragement": "A small kindness can brighten someone's whole day",
        },
        "perseverance": {
            "problem": f"{char_name} couldn't do something that everyone else could do",
            "discovery": "There was a chance to try again, but it seemed impossible.",
            "greeting": "I see you've been practicing. That takes real dedication",
            "advice": "Every expert was once a beginner. Just keep trying",
            "first_attempt": f"{char_name} tried again, focusing on just one small part.",
            "challenge": "The first few tries didn't work, and it felt frustrating.",
            "progress": f"But slowly, {char_name} started to get the hang of it.",
            "success": f"{char_name} finally succeeded after many patient tries!",
            "celebration": "doing a happy dance together",
            "encouragement": "Don't give up! Each try makes you a little bit better",
        },
        "being_different": {
            "problem": f"{char_name} looked a little different from the others",
            "discovery": "The differences that seemed strange were actually quite special.",
            "greeting": "Wow, I've never seen anyone quite like you before - how wonderful",
            "advice": "What makes you different is what makes you uniquely you",
            "first_attempt": f"{char_name} decided to stop hiding and show the real self.",
            "challenge": "Some still stared and whispered at first.",
            "progress": f"But others started to admire what made {char_name} special.",
            "success": f"{char_name}'s unique quality turned out to be a wonderful gift!",
            "celebration": "admiring each other's unique features",
            "encouragement": "Never hide who you are. Your differences are your superpowers",
        },
        "overcoming_fear": {
            "problem": f"{char_name} was very afraid of the dark",
            "discovery": "Something beautiful could only be seen at night!",
            "greeting": "I used to be scared too. Would you like some company",
            "advice": "The dark is just the light taking a rest. There's nothing to fear",
            "first_attempt": f"{char_name} peeked out into the darkness for just a moment.",
            "challenge": "Strange sounds made the fear come rushing back.",
            "progress": f"But slowly, {char_name}'s eyes adjusted and saw beautiful things.",
            "success": f"The night was full of wonders {char_name} had never seen before!",
            "celebration": "watching the stars twinkle together",
            "encouragement": "What seems scary often hides something beautiful",
        },
    }

    return elements.get(theme, elements["friendship"])


def save_story(story: str, filename: str = None, output_dir: str = "stories") -> str:
    """Save story to file."""
    os.makedirs(output_dir, exist_ok=True)

    if filename is None:
        # Extract title from story
        first_line = story.split('\n')[0]
        title = first_line.replace("Title:", "").strip()
        # Convert to filename
        filename = title.lower()
        filename = "".join(c if c.isalnum() or c == ' ' else '' for c in filename)
        filename = filename.replace(' ', '_')[:50]
        filename = f"{filename}.txt"

    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(story)

    return filepath


def list_themes():
    """List available themes."""
    print("\nAvailable Themes:")
    print("-" * 40)
    for theme, data in THEMES.items():
        print(f"  {theme}: {data['moral']}")
    print("-" * 40)


def list_characters():
    """List available characters."""
    print("\nAvailable Characters:")
    print("-" * 40)
    for char_type, name, setting in CHARACTERS:
        print(f"  {name} the {char_type} (lives in {setting})")
    print("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        description="Generate kids stories from prompts"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Story prompt (e.g., 'a shy penguin who makes friends')"
    )
    parser.add_argument(
        "--theme", "-t",
        choices=list(THEMES.keys()),
        help="Story theme"
    )
    parser.add_argument(
        "--character", "-c",
        help="Character type (e.g., 'rabbit', 'penguin')"
    )
    parser.add_argument(
        "--random", "-r",
        action="store_true",
        help="Generate a random story"
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
    parser.add_argument(
        "--output", "-o",
        help="Output filename"
    )
    parser.add_argument(
        "--output-dir",
        default="stories",
        help="Output directory (default: stories)"
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print story without saving"
    )

    args = parser.parse_args()

    if args.list_themes:
        list_themes()
        return

    if args.list_characters:
        list_characters()
        return

    # Find character if specified
    character = None
    if args.character:
        for c in CHARACTERS:
            if args.character.lower() in c[0].lower():
                character = c
                break

    # Generate story
    print("\nGenerating story...")
    story = generate_story_from_template(
        prompt=args.prompt,
        theme=args.theme,
        character=character
    )

    if args.print_only:
        print("\n" + "=" * 60)
        print(story)
        print("=" * 60)
    else:
        filepath = save_story(story, args.output, args.output_dir)
        print(f"Story saved to: {filepath}")
        print("\nFirst few lines:")
        print("-" * 40)
        for line in story.split('\n')[:5]:
            print(line)
        print("...")

    return story


if __name__ == "__main__":
    main()
