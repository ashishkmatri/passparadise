# YouTube Kids Stories Automation - Project Setup Conversation

## Project Motives

### Core Goals

1. **Passive Income via YouTube**
   - Build a kids story channel that generates revenue with minimal ongoing effort
   - Target: 1000 subscribers + 4000 watch hours for monetization
   - Long-term: INR 5,000-20,000/month passive income

2. **Use FREE Resources as Much as Possible**
   - Zero upfront investment (using $19.59 AWS credits)
   - Free TTS: edge-tts (Microsoft neural voices)
   - Free images: Leonardo.ai (150/day), Playground AI (500/day), Pixabay
   - Free music: Pixabay royalty-free
   - Free video processing: FFmpeg

3. **Maximize Quality from Free Tools**
   - **Audio must be best possible** - warm, engaging narration
   - **Video must be entertaining** - visually appealing for kids
   - **A/V must be in perfect sync** - audio matches visuals
   - **Story sync** - narration, images, and storyline flow together seamlessly

### Quality Standards

| Aspect | Requirement |
|--------|-------------|
| **Audio** | Clear, warm voice (en-US-AnaNeural), proper pacing for kids |
| **Video** | 1920x1080, smooth transitions, engaging visuals |
| **A/V Sync** | Each scene image displays exactly while its narration plays |
| **Story Flow** | Images match narration content, logical scene progression |

---

## Project Overview

**Purpose:** Build automated pipeline to generate YouTube Kids story videos (ages 2-6) for passive income.

**Target:**
- Upload 100+ videos in 6 months
- Reach monetization (1000 subs + 4000 watch hours)
- Earn INR 5,000-20,000/month by Year 2

---

## Infrastructure Setup

### 1. AWS CLI Profile Configuration

Created separate AWS profiles for work/personal accounts:

```bash
# Added to ~/.bashrc
aws-personal  # or awsp - Switch to personal account
aws-work      # or awsw - Switch to work account
aws-profile   # or awspr - Show current profile
```

Personal account: `637423452246` (user: ashishsuper)

### 2. Terraform EC2 Deployment

**Architecture:**
- **Spot Instance** (t3.medium) - 60-90% cheaper than on-demand
- **Persistent Data Volume** (30GB) - Survives spot interruptions
- **DLM Hourly Snapshots** - Automated backups, keep last 24

**Resources Created:**
| Resource | Value |
|----------|-------|
| Instance ID | `i-03389c601a2e9e1f0` |
| Public IP | `13.233.45.47` |
| Data Volume | `vol-0aed8e05ad2564618` (30GB) |
| DLM Policy | `policy-0dda5abe915e15279` |

**Estimated Cost:** ~$12-18/month total
- Spot: ~$8-12
- Data volume: ~$2.40
- Snapshots: ~$2-3

**SSH Access:**
```bash
ssh -i ~/.ssh/youtube-ec2-key ubuntu@13.233.45.47
```

### 3. Key Terraform Decisions

**Spot Instance vs On-Demand:**
- Chose spot for 60-90% cost savings
- Trade-off: Can be interrupted with 2-min warning
- Mitigation: Persistent data volume + hourly snapshots

**Separate Data Volume:**
- Root volume (10GB) for OS only - can be deleted
- Data volume (30GB) persists across spot interruptions
- All project files stored on `/data/youtube-automation`

**DLM Snapshots:**
- AWS Data Lifecycle Manager (not cron inside EC2)
- Runs independently of instance state
- Incremental snapshots = low cost (~$2-3/month)
- Hourly frequency, keeps last 24

---

## Python Automation Pipeline

### Project Structure

```
youtube-automation/
├── pipeline.py              # Main orchestrator
├── auto_generate.py         # One-command video generation
├── config.py                # Settings (resolution, paths, voices)
├── requirements.txt         # Python dependencies
├── scripts/
│   ├── __init__.py
│   ├── scene_parser.py      # Extract [SCENE:] markers from story
│   ├── tts_generator.py     # edge-tts voice generation
│   ├── image_generator.py   # Create placeholder images
│   └── video_assembler.py   # FFmpeg video assembly
├── stories/                 # 11 story text files
│   ├── little_star.txt
│   ├── brave_rabbit.txt
│   ├── penny_penguin.txt
│   ├── oliver_owl.txt
│   ├── tilly_turtle.txt
│   ├── ziggy_zebra.txt
│   ├── luna_cloud.txt
│   ├── rosie_garden.txt
│   ├── holiday_christmas_reindeer.txt
│   ├── holiday_diwali_lamp.txt
│   └── holiday_easter_bunny.txt
└── output/                  # Generated videos
```

### Tech Stack (100% FREE)

| Component | Tool |
|-----------|------|
| Text-to-Speech | edge-tts (Microsoft neural voices) |
| Voice | en-US-AnaNeural (warm female) |
| Images | Python Pillow (placeholder starry backgrounds) |
| Video Assembly | FFmpeg |
| Video Format | 1920x1080, 30fps, H.264/AAC |

### Usage

```bash
# List available stories
python3 auto_generate.py --list

# Generate specific story
python3 auto_generate.py --story little_star

# Generate all stories
python3 auto_generate.py --all
```

### Story Format

```
Title: The Little Star Who Found a Friend

[SCENE: A dark night sky filled with twinkling stars of all sizes]
High up in the velvet night sky, thousands of stars twinkled and danced.

[SCENE: A tiny star with a sad face, smaller than all other stars]
Among them was Twinkle, the tiniest star of all...
```

---

## First Successful Video Generation

```
============================================================
YOUTUBE VIDEO GENERATOR
============================================================
Story: /data/youtube-automation/stories/little_star.txt
Output: /data/youtube-automation/output/little_star_20251227_080348.mp4
============================================================

[1/4] Parsing story...
  Title: The Little Star Who Found a Friend
  Scenes: 11

[2/4] Generating voice narration...
  Generated 11 audio files

[3/4] Generating images...
  Generated intro, 11 scenes, outro

[4/4] Assembling video...
  Scene 1-11/11 complete

============================================================
VIDEO GENERATION COMPLETE!
============================================================
Output: /data/youtube-automation/output/little_star_20251227_080348.mp4
Size: 2.0 MB
============================================================
```

---

## Cost Optimization Strategy

| Mode | Monthly Cost | Use Case |
|------|-------------|----------|
| Running 24/7 | ~$15-18 | Active video generation |
| Spot terminated, volume exists | ~$5 | Volume + snapshots only |
| Volume destroyed, snapshots only | ~$2-3 | Long break (restore from snapshot) |

---

## A/V Sync Implementation

### Current Implementation

The pipeline ensures **perfect A/V sync** by:

1. **Scene-based structure:** Each `[SCENE: description]` marker creates one image + one audio clip
2. **Audio-driven timing:** Scene duration = exact length of TTS narration
3. **FFmpeg assembly:** Each scene video is created with `-shortest` flag to match audio duration exactly

```
Scene Flow:
[Image 1] ←→ [Audio 1: "High up in the velvet night sky..."] (4.2 seconds)
[Image 2] ←→ [Audio 2: "Among them was Twinkle..."] (5.1 seconds)
...
```

### Quality Optimization Areas

| Component | Current | Upgrade Path |
|-----------|---------|--------------|
| **TTS Voice** | en-US-AnaNeural | Test other voices (Jenny, Aria) for warmth |
| **Speech Rate** | -10% slower | Fine-tune for kids' comprehension |
| **Images** | Placeholder (starry bg) | Leonardo.ai / Playground AI integration |
| **Transitions** | Hard cuts | Add fade/crossfade effects |
| **Background Music** | None | Soft lullaby from Pixabay (15% volume) |
| **Ken Burns Effect** | None | Subtle pan/zoom on images |

---

## Next Steps

### Immediate (Quality Focus)
1. **Upgrade Images:** Integrate Leonardo.ai API for AI-generated scene images
2. **Add Background Music:** Pixabay royalty-free lullaby music
3. **Add Transitions:** Crossfade between scenes for smoother flow
4. **Test Audio Voices:** Compare different edge-tts voices for best warmth

### Growth
5. **Batch Generate:** Run all 11 stories
6. **YouTube Upload:** Manual initially, automate later
7. **Create More Stories:** Target 100+ videos
8. **SEO Optimization:** Titles, descriptions, tags for discoverability

---

## Quick Reference Commands

```bash
# Switch AWS profile
awsp                    # Personal
awsw                    # Work

# Terraform
cd ~/pers/passincome/youtube-terraform
terraform apply         # Create/update infrastructure
terraform destroy       # Destroy everything

# SSH to server
ssh -i ~/.ssh/youtube-ec2-key ubuntu@13.233.45.47

# Generate videos
cd /data/youtube-automation
python3 auto_generate.py --story little_star
python3 auto_generate.py --all

# Copy files to server
scp -i ~/.ssh/youtube-ec2-key -r ./youtube-automation/* ubuntu@13.233.45.47:/data/youtube-automation/
```

---

*Date: December 27, 2025*
