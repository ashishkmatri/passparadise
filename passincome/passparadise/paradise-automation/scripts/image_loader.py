"""
Image Loader - Load and sort images from user-provided folder
"""
import os
from typing import List
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPPORTED_IMAGE_FORMATS


def load_images_from_folder(
    folder_path: str,
    sort_by: str = "date_modified"
) -> List[str]:
    """
    Load images from a folder and sort them.

    Args:
        folder_path: Path to folder containing images
        sort_by: Sorting method - "date_modified", "filename", "random"

    Returns:
        List of absolute paths to images, sorted as specified
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"Folder not found: {folder_path}")

    # Get all image files
    images = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(SUPPORTED_IMAGE_FORMATS):
            images.append(os.path.join(folder_path, filename))

    if not images:
        raise ValueError(f"No images found in {folder_path}")

    # Sort based on method
    if sort_by == "date_modified":
        images.sort(key=lambda x: os.path.getmtime(x))
    elif sort_by == "filename":
        images.sort(key=lambda x: os.path.basename(x).lower())
    elif sort_by == "random":
        import random
        random.shuffle(images)
    else:
        raise ValueError(f"Unknown sort method: {sort_by}")

    return images


def get_image_info(image_path: str) -> dict:
    """Get basic info about an image."""
    from PIL import Image

    with Image.open(image_path) as img:
        return {
            "path": image_path,
            "filename": os.path.basename(image_path),
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load images from folder")
    parser.add_argument("folder", help="Path to images folder")
    parser.add_argument("--sort", default="date_modified",
                       choices=["date_modified", "filename", "random"],
                       help="Sort method")

    args = parser.parse_args()

    images = load_images_from_folder(args.folder, args.sort)
    print(f"Found {len(images)} images:")
    for img in images:
        print(f"  {os.path.basename(img)}")
