import os
import json
import subprocess
from core.presets import FORMAT_CONFIG, RESOLUTION_VALUES, CHANNEL_VALUES
from core.ffmpeg_resolver import get_ffmpeg_path, get_ffprobe_path


def _no_window():
    return subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


def probe_duration(input_path: str) -> float:
    try:
        result = subprocess.run(
            [get_ffprobe_path(), '-v', 'quiet', '-print_format', 'json', '-show_format', input_path],
            capture_output=True, text=True, timeout=30,
            creationflags=_no_window(),
        )
        data = json.loads(result.stdout)
        return float(data['format'].get('duration', 0))
    except Exception:
        return 0.0


def _parse_resolution(res: str) -> str | None:
    """Return ffmpeg scale value 'W:H', or None to skip scaling."""
    if res in RESOLUTION_VALUES:
        return RESOLUTION_VALUES[res]           # None for 'Original'
    # Custom input: accept '1920x1080' or '1920:1080'
    normalized = res.strip().replace('x', ':').replace('X', ':')
    parts = normalized.split(':')
    if len(parts) == 2 and all(p.strip().isdigit() and int(p) > 0 for p in parts):
        return normalized
    return None                                 # invalid → skip


def build_command(input_path: str, output_path: str, params: dict) -> list:
    fmt = params.get('format', 'MP4')
    config = FORMAT_CONFIG.get(fmt, {})
    fmt_type = config.get('type', 'video')

    cmd = [get_ffmpeg_path(), '-y', '-i', input_path, '-progress', 'pipe:1', '-nostats']

    if fmt == 'GIF':
        fps = params.get('framerate', 'Original')
        if fps == 'Original':
            fps = '10'
        res = params.get('resolution', 'Original')
        scale_val = _parse_resolution(res)
        scale_part = f'scale={scale_val}:flags=lanczos' if scale_val else 'scale=iw:ih:flags=lanczos'
        vf = f'fps={fps},{scale_part},split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse'
        cmd += ['-vf', vf, output_path]
        return cmd

    if fmt_type == 'video':
        vcodec = params.get('vcodec', 'libx264')
        cmd += ['-c:v', vcodec]

        scale_val = _parse_resolution(params.get('resolution', 'Original'))
        if scale_val:
            cmd += ['-vf', f'scale={scale_val}']

        fps = params.get('framerate', 'Original')
        if fps != 'Original':
            cmd += ['-r', fps]

        vbitrate = params.get('vbitrate', 'Auto')
        if vbitrate != 'Auto':
            cmd += ['-b:v', vbitrate]

        acodec = params.get('acodec', 'aac')
        cmd += ['-c:a', acodec]

        abitrate = params.get('abitrate', 'Auto')
        if abitrate != 'Auto':
            cmd += ['-b:a', abitrate]

        samplerate = params.get('samplerate', 'Original')
        if samplerate != 'Original':
            cmd += ['-ar', samplerate]

        ch = CHANNEL_VALUES.get(params.get('channels', 'Original'))
        if ch:
            cmd += ['-ac', ch]

    else:  # audio only
        cmd += ['-vn']
        cmd += ['-c:a', params.get('acodec', 'aac')]

        abitrate = params.get('abitrate', 'Auto')
        if abitrate != 'Auto':
            cmd += ['-b:a', abitrate]

        samplerate = params.get('samplerate', 'Original')
        if samplerate != 'Original':
            cmd += ['-ar', samplerate]

        ch = CHANNEL_VALUES.get(params.get('channels', 'Original'))
        if ch:
            cmd += ['-ac', ch]

    cmd.append(output_path)
    return cmd
