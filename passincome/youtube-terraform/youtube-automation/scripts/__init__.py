"""
YouTube Kids Stories Automation - Scripts Module
"""
from .scene_parser import parse_story, load_story_from_file, get_scene_duration
from .tts_generator import generate_audio_sync, generate_all_scenes_sync
from .image_generator import generate_all_images, create_title_card, create_outro_card
from .video_assembler import assemble_full_video, add_background_music

__all__ = [
    'parse_story',
    'load_story_from_file',
    'get_scene_duration',
    'generate_audio_sync',
    'generate_all_scenes_sync',
    'generate_all_images',
    'create_title_card',
    'create_outro_card',
    'assemble_full_video',
    'add_background_music',
]
