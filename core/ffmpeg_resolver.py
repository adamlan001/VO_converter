import os
import shutil
import sys


def _app_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_ffmpeg_path() -> str:
    local = os.path.join(_app_dir(), 'bin', 'ffmpeg.exe')
    if os.path.isfile(local):
        return local
    found = shutil.which('ffmpeg')
    return found if found else 'ffmpeg'


def get_ffprobe_path() -> str:
    local = os.path.join(_app_dir(), 'bin', 'ffprobe.exe')
    if os.path.isfile(local):
        return local
    found = shutil.which('ffprobe')
    return found if found else 'ffprobe'


def is_ffmpeg_available() -> bool:
    local = os.path.join(_app_dir(), 'bin', 'ffmpeg.exe')
    if os.path.isfile(local):
        return True
    return bool(shutil.which('ffmpeg'))
