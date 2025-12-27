#!/usr/bin/env python3
"""
PassParadise - Romantic Image Slideshow Video Generator

Quick generation script - wrapper around pipeline.py

Usage:
    python generate.py /path/to/images/
    python generate.py /path/to/images/ --music slow_burn
    python generate.py /path/to/images/ --youtube-audio "https://youtube.com/..."
"""
from pipeline import main

if __name__ == "__main__":
    main()
