import os
import subprocess
from core.ffmpeg_resolver import get_ffmpeg_path

# encoder name -> (label, brand)
HW_ENCODER_INFO: dict[str, tuple[str, str]] = {
    'h264_nvenc': ('H.264 NVENC', 'NVIDIA'),
    'hevc_nvenc': ('H.265 NVENC', 'NVIDIA'),
    'h264_amf':   ('H.264 AMF',   'AMD'),
    'hevc_amf':   ('H.265 AMF',   'AMD'),
    'h264_qsv':   ('H.264 QSV',   'Intel'),
    'hevc_qsv':   ('H.265 QSV',   'Intel'),
}

# which HW encoders make sense for each output format
FORMAT_HW_CODECS: dict[str, list[str]] = {
    'MP4':  ['h264_nvenc', 'hevc_nvenc', 'h264_amf', 'hevc_amf', 'h264_qsv', 'hevc_qsv'],
    'MKV':  ['h264_nvenc', 'hevc_nvenc', 'h264_amf', 'hevc_amf', 'h264_qsv', 'hevc_qsv'],
    'MOV':  ['h264_nvenc', 'hevc_nvenc', 'h264_amf', 'hevc_amf', 'h264_qsv', 'hevc_qsv'],
    'AVI':  ['h264_nvenc', 'h264_amf', 'h264_qsv'],
    'WebM': [],
    'GIF':  [],
}


def detect() -> set[str]:
    """Query ffmpeg -encoders and return available HW encoder names."""
    try:
        result = subprocess.run(
            [get_ffmpeg_path(), '-hide_banner', '-encoders'],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
        )
        return {enc for enc in HW_ENCODER_INFO if enc in result.stdout}
    except Exception:
        return set()


def brand_summary(available: set[str]) -> str:
    """Return e.g. 'NVIDIA、AMD' from detected encoder set."""
    brands: list[str] = []
    for brand in ('NVIDIA', 'AMD', 'Intel'):
        if any(HW_ENCODER_INFO[e][1] == brand for e in available if e in HW_ENCODER_INFO):
            brands.append(brand)
    return '、'.join(brands)
