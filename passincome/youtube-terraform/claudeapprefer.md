📋 Copy-Paste This to VS Code Claude

## YouTube Kids Stories Automation Project - Context

### 1. STORY FORMAT
- **Type**: Bedtime stories, moral stories, educational tales for kids aged 2-6
- **Length**: 3-5 minutes per video (12-14 scenes)
- **Themes**: 
  - Evergreen: Friendship, courage, kindness, overcoming fears, being different
  - Holiday: Christmas, Diwali, Halloween, Easter, New Year, etc.
- **Structure**: Each story has [SCENE: image description] markers for automation
- **Characters**: Cute animals (penguins, rabbits, owls, stars, turtles)

### 2. VIDEO STRUCTURE
- **Format**: Image slideshow with TTS narration
- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30 FPS
- **Animation**: Twinkling stars background, pulsing glow effects, Ken Burns (pan/zoom)
- **Audio**: edge-tts (Microsoft neural voices) for narration
- **Music**: Royalty-free background music from Pixabay
- **Intro**: 3 second title card with animated stars
- **Outro**: 4 second "The End" card with subscribe CTA

### 3. TECH STACK
- **TTS**: edge-tts (free Microsoft voices) - en-US-AnaNeural for warm female voice
- **Images**: Placeholder generation with Pillow/NumPy (upgrade to Leonardo.ai API later)
- **Video**: FFmpeg for assembly
- **Animation**: Python + Pillow for frame generation
- **OS**: Ubuntu 22.04 on AWS EC2 t3.medium (4GB RAM)

### 4. KEY SCRIPTS STRUCTURE
```python
# Main pipeline.py structure
youtube-automation/
├── pipeline.py              # Main orchestrator
├── auto_generate.py         # One-command video generation
├── config.py                # Settings (resolution, paths)
├── api_keys.json            # API keys for online services
├── requirements.txt         # Dependencies
├── scripts/
│   ├── scene_parser.py      # Parse [SCENE:] markers from stories
│   ├── tts_generator.py     # edge-tts voice generation
│   ├── image_generator.py   # Create/fetch images
│   └── video_assembler.py   # FFmpeg video assembly
├── stories/                 # Story text files (17 total)
│   ├── little_star.txt
│   ├── brave_rabbit.txt
│   ├── penny_penguin_friend.txt
│   ├── holiday_christmas_reindeer.txt
│   └── ... (8 evergreen + 9 holiday)
└── output/                  # Generated videos
```

### 5. SAMPLE STORY FORMAT (little_star.txt)
Title: The Little Star Who Found a Friend
[SCENE: A dark night sky filled with twinkling stars of all sizes]
High up in the velvet night sky, thousands of stars twinkled and danced.
[SCENE: A tiny star with a sad face, smaller than all other stars around it]
Among them was Twinkle, the tiniest star of all. She often felt lonely because the other stars seemed so far away.
[SCENE: A little girl with pigtails looking out her bedroom window at the stars]
Down on Earth, a little girl named Maya loved to watch the stars from her window every night.
... (continues for 12-14 scenes)

### 6. DEPENDENCIES (requirements.txt)
edge-tts
Pillow
numpy
pydub
requests

### 7. HOSTING
- **Current**: AWS EC2 t3.medium with $19.59 free credits
- **Terraform**: IaC scripts for start/stop/backup/destroy lifecycle
- **Cost strategy**: Start→Work→Stop (save 90%), Backup→Destroy (save 95%)

### 8. MONETIZATION TIMELINE
- Month 1-6: Build content (100+ videos), likely ₹0 earnings
- Month 6-12: Reach 1000 subs + 4000 watch hours for monetization
- Year 2+: Potential ₹5,000-₹20,000/month passive income

### 9. WHAT I NEED NOW
1. Regenerate all Python automation scripts
2. Deploy EC2 using Terraform
3. Generate first batch of videos

📋 Also Copy This Code Snippet
TTS Generator (core function)
pythonimport edge_tts
import asyncio

async def generate_voice(text, output_path, voice="en-US-AnaNeural"):
    """Generate TTS audio using edge-tts"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path

# Usage
asyncio.run(generate_voice("Hello little friends!", "scene_01.mp3"))
Video Assembly (FFmpeg)
pythonimport subprocess

def create_video_from_images(images, durations, audio_path, output_path):
    """Combine images + audio into video"""
    # Create slideshow
    filter_parts = []
    for i, (img, dur) in enumerate(zip(images, durations)):
        filter_parts.append(f"[{i}:v]scale=1920:1080,setsar=1[v{i}]")
    
    subprocess.run([
        'ffmpeg', '-y',
        # ... inputs and filters
        '-c:v', 'libx264', '-c:a', 'aac',
        output_path
    ])

Copy everything above and paste into VS Code Claude! 🚀has to be free sources as much as possible. mention the purpose , which is passive income. target and all the things we discussed. IGNORE-> WSL issues, storage issue , troubleshooting we did for laptop which is irrelevant as we are now using ec212:46 PMSynthesized YouTube automation project scope using free resources for passive income.The user wants a clean, focused summary for VS Code Claude that:

Focuses ONLY on the YouTube automation project
Mentions purpose (passive income)
All free tools/sources
Ignores WSL issues, storage problems, laptop troubleshooting
EC2 focused now

Let me create a comprehensive but clean context document.📋 Copy-Paste This to VS Code Claude

## PROJECT: YouTube Kids Stories Automation for Passive Income

### PURPOSE
Build automated pipeline to generate YouTube Kids story videos (ages 2-6) for passive income. Target: Upload 100+ videos in 6 months, reach monetization (1000 subs + 4000 watch hours), earn ₹5,000-₹20,000/month by Year 2.

### TARGET AUDIENCE
- Kids aged 2-6 years
- Parents looking for safe, educational content
- Global English-speaking audience

### INVESTMENT & TIMELINE
- Initial: ~₹0 (using $19.59 AWS credits = 4-6 months free)
- Month 1-6: Build content, ₹0 earnings (not monetized yet)
- Month 7-12: Monetization approved, ₹500-₹5,000/month
- Year 2+: ₹5,000-₹20,000/month passive income

### HOSTING
- AWS EC2 t3.medium (4GB RAM, 2 vCPU, 30GB storage)
- Ubuntu 22.04 LTS
- Terraform IaC for cost optimization (start/stop/backup/destroy lifecycle)

---

## CONTENT STRATEGY

### STORY TYPES (17 Stories Ready)

**Evergreen (8)** - Upload anytime, views forever:
1. The Little Star Who Found a Friend - Friendship
2. Brave Little Rabbit - Courage/facing fears
3. Penny the Shy Penguin - Making friends/shyness
4. Oliver Owl's Night Light - Overcoming fear of dark
5. Rosie Rabbit's Magic Garden - Kindness/sharing
6. Ziggy Zebra's Special Stripes - Being different/acceptance
7. Tilly Turtle Learns to Swim - Perseverance/never give up
8. Luna the Sleepy Cloud - Bedtime/sleep story

**Holiday (9)** - Upload 3 weeks before, earns 3-5x more:
1. Christmas - Rudy the Little Reindeer (Dec 1)
2. Halloween - Casper the Friendly Ghost (Oct 1)
3. Easter - Bella Bunny's Egg Hunt (3 weeks before)
4. Diwali - Diya the Little Lamp (2 weeks before)
5. Hanukkah - Danny Dreidel's Miracle (2 weeks before)
6. New Year - Benny Balloon's Big Night (Dec 20)
7. Thanksgiving - Tommy Turkey's Thank You (Nov 1)
8. Valentine's Day - Teddy Bear's Heart (Feb 1)
9. St. Patrick's Day - Lucky Leprechaun (Mar 1)

### STORY FORMAT
- Length: 3-5 minutes (12-14 scenes per story)
- Structure: [SCENE: image prompt] followed by narration text
- Characters: Cute animals (stars, rabbits, penguins, owls)
- Themes: Moral lessons, bedtime comfort, educational

### SAMPLE STORY FORMAT
Title: The Little Star Who Found a Friend
[SCENE: A dark night sky filled with twinkling stars of all sizes]
High up in the velvet night sky, thousands of stars twinkled and danced.
[SCENE: A tiny star with a sad face, smaller than all other stars]
Among them was Twinkle, the tiniest star of all. She often felt lonely.
[SCENE: A little girl looking out her bedroom window at stars]
Down on Earth, a little girl named Maya loved watching stars every night.
... (12-14 scenes total)
[SCENE: The star and girl both smiling, connected by a beam of light]
The End.

---

## TECH STACK (100% FREE)

### Text-to-Speech
- **Tool**: edge-tts (Microsoft neural voices, FREE unlimited)
- **Voice**: en-US-AnaNeural (warm female, storyteller style)
- **Alternative**: espeak-ng (offline, robotic - fallback only)

### Image Generation
- **Free Options**:
  - Leonardo.ai - 150 images/day FREE
  - Playground AI - 500 images/day FREE
  - Microsoft Designer - FREE with Microsoft account
  - Pixabay - FREE stock illustrations
- **Placeholder**: Python Pillow/NumPy (gradient backgrounds + stars)

### Video Assembly
- **Tool**: FFmpeg (FREE, open source)
- **Format**: 1920x1080, 30fps, H.264 video, AAC audio

### Background Music
- **Source**: Pixabay Music (100% FREE, royalty-free)
- **Style**: Soft lullaby, gentle piano, magical chimes

---

## VIDEO STRUCTURE

| Section | Duration | Content |
|---------|----------|---------|
| Intro | 3 sec | Animated title card with twinkling stars |
| Story | 3-5 min | 12-14 scenes with narration |
| Outro | 4 sec | "The End" + Subscribe CTA |

### ANIMATION EFFECTS
- Twinkling background stars (varying brightness)
- Special star with pulsing glow (main character highlight)
- Ken Burns effect (subtle pan/zoom on images)
- Smooth transitions between scenes

---

## PROJECT STRUCTURE
youtube-automation/
├── pipeline.py              # Main orchestrator
├── auto_generate.py         # One-command: story idea → finished video
├── config.py                # Settings (resolution, paths, voices)
├── api_keys.json            # API keys for Leonardo.ai, etc.
├── requirements.txt         # Python dependencies
├── scripts/
│   ├── scene_parser.py      # Extract [SCENE:] markers from story
│   ├── tts_generator.py     # edge-tts voice generation
│   ├── image_generator.py   # Fetch/generate images
│   └── video_assembler.py   # FFmpeg video assembly
├── stories/                 # 17 story text files
│   ├── little_star.txt
│   ├── brave_rabbit.txt
│   ├── penny_penguin_friend.txt
│   ├── holiday_christmas_reindeer.txt
│   └── ... (8 evergreen + 9 holiday)
└── output/                  # Generated videos

---

## DEPENDENCIES (requirements.txt)
edge-tts
Pillow
numpy
pydub
requests
aiohttp

System packages (Ubuntu):
```bash
apt install python3 python3-pip ffmpeg espeak-ng git
```

---

## CORE CODE SNIPPETS

### TTS Generation
```python
import edge_tts
import asyncio

async def generate_voice(text, output_path, voice="en-US-AnaNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path
```

### Scene Parser
```python
import re

def parse_story(story_text):
    scenes = []
    pattern = r'\[SCENE:\s*([^\]]+)\]\s*([^\[]+)'
    matches = re.findall(pattern, story_text, re.DOTALL)
    for image_prompt, narration in matches:
        scenes.append({
            'image_prompt': image_prompt.strip(),
            'narration': narration.strip()
        })
    return scenes
```

### Video Assembly
```python
import subprocess

def assemble_video(image_files, audio_file, output_path):
    # Create video from images with audio
    subprocess.run([
        'ffmpeg', '-y',
        '-loop', '1', '-t', duration, '-i', image,
        '-i', audio_file,
        '-c:v', 'libx264', '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        output_path
    ])
```

---

## YOUTUBE SEO STRATEGY

### Title Format
[Emoji] Story Name | Bedtime Stories for Kids | [Theme] Story
Example: 🌟 The Little Star | Bedtime Stories for Kids | Friendship Story

### Tags
bedtime stories, kids stories, stories for children, moral stories,
bedtime stories for toddlers, sleep stories, children's stories,
animated stories, story time, preschool stories

### Description Template
🌙 [Story Name] - A magical bedtime story for kids!
Join [Character] on an adventure about [theme]...
✨ Perfect for:

Bedtime routine
Quiet time
Learning about [moral]

👍 Like & Subscribe for more stories!
#BedtimeStories #KidsStories #StoriesForChildren

---

## UPLOAD SCHEDULE

- **Target**: 3-5 videos per week
- **Best times**: 6-8 PM (bedtime routine)
- **Holiday videos**: Upload 3 weeks before holiday
- **Goal**: 100+ videos in first 6 months

---

## REVENUE PROJECTION

| Period | Videos | Subscribers | Watch Hours | Monthly Earnings |
|--------|--------|-------------|-------------|------------------|
| Month 1-3 | 50 | 200-400 | 1,000 | ₹0 |
| Month 4-6 | 100 | 600-1,000 | 3,000 | ₹0 |
| Month 7-12 | 150 | 1,500-3,000 | 6,000 | ₹2,000-₹5,000 |
| Year 2 | 250+ | 5,000-10,000 | 20,000+ | ₹5,000-₹20,000 |

---

## WHAT I NEED

1. **Regenerate all Python automation scripts** (pipeline.py, scene_parser.py, tts_generator.py, image_generator.py, video_assembler.py)
2. **Generate all 17 story text files** (8 evergreen + 9 holiday)
3. **Create config and requirements files**
4. **Help test end-to-end video generation**

All using FREE tools only!

Copy everything above and paste into VS Code Claude! 🚀