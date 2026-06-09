VIDEO_FORMATS = ['MP4', 'MKV', 'MOV', 'AVI', 'WebM', 'GIF']
AUDIO_FORMATS = ['MP3', 'AAC', 'WAV', 'FLAC', 'OGG', 'M4A']

FORMAT_CONFIG = {
    'MP4':  {'ext': 'mp4',  'type': 'video', 'vcodecs': ['libx264', 'libx265', 'copy'], 'acodecs': ['aac', 'libmp3lame', 'copy']},
    'MKV':  {'ext': 'mkv',  'type': 'video', 'vcodecs': ['libx264', 'libx265', 'libvpx-vp9', 'copy'], 'acodecs': ['aac', 'libvorbis', 'copy']},
    'MOV':  {'ext': 'mov',  'type': 'video', 'vcodecs': ['libx264', 'prores_ks', 'copy'], 'acodecs': ['aac', 'copy']},
    'AVI':  {'ext': 'avi',  'type': 'video', 'vcodecs': ['libx264', 'mpeg4', 'copy'], 'acodecs': ['libmp3lame', 'pcm_s16le', 'copy']},
    'WebM': {'ext': 'webm', 'type': 'video', 'vcodecs': ['libvpx-vp9', 'libvpx'], 'acodecs': ['libvorbis', 'libopus']},
    'GIF':  {'ext': 'gif',  'type': 'video', 'vcodecs': [], 'acodecs': []},
    'MP3':  {'ext': 'mp3',  'type': 'audio', 'acodecs': ['libmp3lame'], 'vcodecs': []},
    'AAC':  {'ext': 'aac',  'type': 'audio', 'acodecs': ['aac'], 'vcodecs': []},
    'WAV':  {'ext': 'wav',  'type': 'audio', 'acodecs': ['pcm_s16le', 'pcm_s24le', 'pcm_f32le'], 'vcodecs': []},
    'FLAC': {'ext': 'flac', 'type': 'audio', 'acodecs': ['flac'], 'vcodecs': []},
    'OGG':  {'ext': 'ogg',  'type': 'audio', 'acodecs': ['libvorbis', 'libopus'], 'vcodecs': []},
    'M4A':  {'ext': 'm4a',  'type': 'audio', 'acodecs': ['aac'], 'vcodecs': []},
}

RESOLUTIONS = ['Original', '3840x2160 (4K)', '2560x1440 (2K)', '1920x1080 (FHD)', '1280x720 (HD)', '854x480', '640x360', 'Custom']
RESOLUTION_VALUES = {
    'Original':        None,
    '3840x2160 (4K)':  '3840:2160',
    '2560x1440 (2K)':  '2560:1440',
    '1920x1080 (FHD)': '1920:1080',
    '1280x720 (HD)':   '1280:720',
    '854x480':         '854:480',
    '640x360':         '640:360',
}

FRAMERATES = ['Original', '60', '30', '25', '24', '15', '10', 'Custom']
VIDEO_BITRATES = ['Auto', '20000k', '8000k', '4000k', '2000k', '1000k', '500k']
AUDIO_BITRATES = ['Auto', '320k', '256k', '192k', '128k', '96k', '64k']
SAMPLERATES = ['Original', '48000', '44100', '22050', '16000']
CHANNELS = ['Original', 'Mono', 'Stereo']
CHANNEL_VALUES = {'Original': None, 'Mono': '1', 'Stereo': '2'}
