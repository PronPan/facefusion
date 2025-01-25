import glob
import os
import shutil
import time
from typing import List, Optional

import facefusion.choices
from facefusion import logger

def _error_handler(func, *args, retries=3, delay=1, **kwargs):
    for attempt in range(retries):
        try:
            result = func(*args, **kwargs)
            if attempt > 0:
                logger.debug(f"Success on attempt {attempt+1}/{retries} for {func.__name__}", __name__)
            return result
        except Exception as e:
            logger.debug(f"Error on attempt {attempt+1}/{retries} for {func.__name__}: {str(e)}", __name__)
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

def is_file(file_path: str) -> bool:
    return bool(file_path and _error_handler(os.path.isfile, file_path))

def is_directory(directory_path: str) -> bool:
    return bool(directory_path and _error_handler(os.path.isdir, directory_path))

def get_file_size(file_path: str) -> int:
    return _error_handler(os.path.getsize, file_path) if is_file(file_path) else 0

def get_file_name(file_path: str) -> Optional[str]:
    name, _ = os.path.splitext(os.path.basename(file_path))
    return name if name else None

def get_file_extension(file_path: str) -> Optional[str]:
    _, extension = os.path.splitext(file_path)
    return extension.lower() if extension else None

def get_file_format(file_path: str) -> Optional[str]:
    extension = get_file_extension(file_path)
    if not extension:
        return None
    return {
        '.jpg': 'jpeg',
        '.tif': 'tiff'
    }.get(extension, extension.lstrip('.'))

def same_file_extension(first_path: str, second_path: str) -> bool:
    return get_file_extension(first_path) == get_file_extension(second_path)

def _is_media_type(path: str, formats: List[str]) -> bool:
    return is_file(path) and get_file_format(path) in formats

def is_audio(audio_path: str) -> bool:
    return _is_media_type(audio_path, facefusion.choices.audio_formats)

def has_audio(audio_paths: List[str]) -> bool:
    return any(map(is_audio, audio_paths)) if audio_paths else False

def are_audios(audio_paths: List[str]) -> bool:
    return all(map(is_audio, audio_paths)) if audio_paths else False

def is_image(image_path: str) -> bool:
    return _is_media_type(image_path, facefusion.choices.image_formats)

def has_image(image_paths: List[str]) -> bool:
    return any(map(is_image, image_paths)) if image_paths else False

def are_images(image_paths: List[str]) -> bool:
    return all(map(is_image, image_paths)) if audio_paths else False

def is_video(video_path: str) -> bool:
    return _is_media_type(video_path, facefusion.choices.video_formats)

def has_video(video_paths: List[str]) -> bool:
    return any(map(is_video, video_paths)) if video_paths else False

def are_videos(video_paths: List[str]) -> bool:
    return all(map(is_video, video_paths)) if video_paths else False

def filter_audio_paths(paths: List[str]) -> List[str]:
    return [p for p in paths if is_audio(p)] if paths else []

def filter_image_paths(paths: List[str]) -> List[str]:
    return [p for p in paths if is_image(p)] if paths else []

def _file_operation(operation, src, dest, success_condition):
    _error_handler(operation, src, dest)
    return success_condition()

def copy_file(file_path: str, move_path: str) -> bool:
    return _file_operation(shutil.copy, file_path, move_path, lambda: is_file(move_path)) if is_file(file_path) else False

def move_file(file_path: str, move_path: str) -> bool:
    return _file_operation(shutil.move, file_path, move_path, lambda: not is_file(file_path) and is_file(move_path)) if is_file(file_path) else False

def remove_file(file_path: str) -> bool:
    return _file_operation(os.remove, file_path, None, lambda: not is_file(file_path)) if is_file(file_path) else False

def resolve_file_paths(directory_path: str) -> List[str]:
    if not is_directory(directory_path):
        return []
    entries = _error_handler(os.listdir, directory_path)
    return [
        os.path.join(directory_path, entry)
        for entry in sorted(entries)
        if not entry.startswith(('.', '__'))
    ]

def resolve_file_pattern(file_pattern: str) -> List[str]:
    return sorted(_error_handler(glob.glob, file_pattern)) if in_directory(file_pattern) else []

def in_directory(file_path: str) -> bool:
    if not file_path:
        return False
    dir_path = os.path.dirname(file_path)
    return bool(dir_path and not is_directory(file_path) and is_directory(dir_path))

def create_directory(directory_path: str) -> bool:
    if not directory_path or is_file(directory_path):
        return False
    _error_handler(os.makedirs, directory_path, exist_ok=True)
    return is_directory(directory_path)

def remove_directory(directory_path: str) -> bool:
    if not is_directory(directory_path):
        return False
    _error_handler(shutil.rmtree, directory_path, ignore_errors=True)
    return not is_directory(directory_path)

def resolve_relative_path(path: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))
