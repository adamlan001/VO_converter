from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QButtonGroup, QRadioButton, QFormLayout, QLineEdit,
)
from PyQt6.QtCore import pyqtSignal
from core.presets import (
    VIDEO_FORMATS, AUDIO_FORMATS, FORMAT_CONFIG,
    RESOLUTIONS, FRAMERATES, VIDEO_BITRATES, AUDIO_BITRATES, SAMPLERATES, CHANNELS,
)
from core import hw_detect


class FormatPanel(QWidget):
    params_changed = pyqtSignal()

    def __init__(self, hw_encoders: set[str] | None = None):
        super().__init__()
        self._hw_encoders: set[str] = hw_encoders or set()
        self._setup_ui()
        self._refresh_format_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ── output type ───────────────────────────────────────────────────────
        type_group = QGroupBox('Output Type')
        type_layout = QHBoxLayout(type_group)
        self._type_bg = QButtonGroup(self)
        self._video_rb = QRadioButton('Video')
        self._audio_rb = QRadioButton('Audio')
        self._video_rb.setChecked(True)
        self._type_bg.addButton(self._video_rb, 0)
        self._type_bg.addButton(self._audio_rb, 1)
        self._video_rb.toggled.connect(self._refresh_format_list)
        type_layout.addWidget(self._video_rb)
        type_layout.addWidget(self._audio_rb)
        layout.addWidget(type_group)

        # ── format ────────────────────────────────────────────────────────────
        fmt_group = QGroupBox('Output Format')
        fmt_layout = QFormLayout(fmt_group)
        self._fmt_combo = QComboBox()
        self._fmt_combo.currentTextChanged.connect(self._on_format_changed)
        fmt_layout.addRow('Format:', self._fmt_combo)
        layout.addWidget(fmt_group)

        # ── video settings ────────────────────────────────────────────────────
        self._video_group = QGroupBox('Video Settings')
        vl = QFormLayout(self._video_group)

        self._vcodec_combo = QComboBox()
        vl.addRow('Video Codec:', self._vcodec_combo)

        # Resolution row with optional custom input
        res_row = QWidget()
        res_hl = QHBoxLayout(res_row)
        res_hl.setContentsMargins(0, 0, 0, 0)
        res_hl.setSpacing(4)
        self._resolution_combo = QComboBox()
        self._resolution_combo.addItems(RESOLUTIONS)
        self._resolution_input = QLineEdit()
        self._resolution_input.setPlaceholderText('e.g. 1920x1080')
        self._resolution_input.setVisible(False)
        res_hl.addWidget(self._resolution_combo)
        res_hl.addWidget(self._resolution_input, 1)
        self._resolution_combo.currentTextChanged.connect(
            lambda t: self._resolution_input.setVisible(t == 'Custom'))
        vl.addRow('Resolution:', res_row)

        # Frame rate row with optional custom input
        fps_row = QWidget()
        fps_hl = QHBoxLayout(fps_row)
        fps_hl.setContentsMargins(0, 0, 0, 0)
        fps_hl.setSpacing(4)
        self._framerate_combo = QComboBox()
        self._framerate_combo.addItems(FRAMERATES)
        self._framerate_input = QLineEdit()
        self._framerate_input.setPlaceholderText('e.g. 23.976')
        self._framerate_input.setVisible(False)
        fps_hl.addWidget(self._framerate_combo)
        fps_hl.addWidget(self._framerate_input, 1)
        self._framerate_combo.currentTextChanged.connect(
            lambda t: self._framerate_input.setVisible(t == 'Custom'))
        vl.addRow('Frame Rate:', fps_row)

        self._vbitrate_combo = QComboBox()
        self._vbitrate_combo.addItems(VIDEO_BITRATES)
        vl.addRow('Video Bitrate:', self._vbitrate_combo)

        self._gpu_label = QLabel()
        self._gpu_label.setStyleSheet('font-size: 11px; padding-top: 2px;')
        vl.addRow('', self._gpu_label)
        layout.addWidget(self._video_group)

        # ── audio settings ────────────────────────────────────────────────────
        self._audio_group = QGroupBox('Audio Settings')
        al = QFormLayout(self._audio_group)
        self._acodec_combo = QComboBox()
        self._abitrate_combo = QComboBox()
        self._abitrate_combo.addItems(AUDIO_BITRATES)
        self._samplerate_combo = QComboBox()
        self._samplerate_combo.addItems(SAMPLERATES)
        self._channels_combo = QComboBox()
        self._channels_combo.addItems(CHANNELS)
        al.addRow('Audio Codec:', self._acodec_combo)
        al.addRow('Audio Bitrate:', self._abitrate_combo)
        al.addRow('Sample Rate (Hz):', self._samplerate_combo)
        al.addRow('Channels:', self._channels_combo)
        layout.addWidget(self._audio_group)

        layout.addStretch()

    # ── slots ─────────────────────────────────────────────────────────────────

    def _refresh_format_list(self):
        self._fmt_combo.blockSignals(True)
        self._fmt_combo.clear()
        self._fmt_combo.addItems(VIDEO_FORMATS if self._video_rb.isChecked() else AUDIO_FORMATS)
        self._fmt_combo.blockSignals(False)
        self._on_format_changed(self._fmt_combo.currentText())

    def _on_format_changed(self, fmt: str):
        config = FORMAT_CONFIG.get(fmt, {})
        fmt_type = config.get('type', 'video')
        is_gif = fmt == 'GIF'

        self._acodec_combo.blockSignals(True)
        self._acodec_combo.clear()
        acodecs = config.get('acodecs', [])
        if acodecs:
            self._acodec_combo.addItems(acodecs)
        self._acodec_combo.blockSignals(False)

        # vcodec: SW codecs first, then detected HW codecs with separator
        self._vcodec_combo.blockSignals(True)
        self._vcodec_combo.clear()
        sw_codecs = config.get('vcodecs', [])
        if sw_codecs:
            self._vcodec_combo.addItems(sw_codecs)
        hw_candidates = hw_detect.FORMAT_HW_CODECS.get(fmt, [])
        available_hw = [enc for enc in hw_candidates if enc in self._hw_encoders]
        if available_hw:
            self._vcodec_combo.insertSeparator(self._vcodec_combo.count())
            for enc in available_hw:
                label, brand = hw_detect.HW_ENCODER_INFO[enc]
                self._vcodec_combo.addItem(f'{enc}  [{brand} GPU]', userData=enc)
        self._vcodec_combo.blockSignals(False)

        # GPU status label
        if fmt_type == 'video' and not is_gif:
            if available_hw:
                brands = hw_detect.brand_summary(set(available_hw))
                self._gpu_label.setText(f'GPU acceleration available: {brands}')
                self._gpu_label.setStyleSheet('font-size: 11px; color: #2e7d32;')
            else:
                self._gpu_label.setText('No GPU acceleration (CPU encoding)')
                self._gpu_label.setStyleSheet('font-size: 11px; color: #888;')
        else:
            self._gpu_label.setText('')

        self._video_group.setVisible(fmt_type == 'video')
        self._audio_group.setVisible(fmt_type == 'audio' or (fmt_type == 'video' and not is_gif))
        self._vcodec_combo.setEnabled(not is_gif)
        self._vbitrate_combo.setEnabled(not is_gif)

        self.params_changed.emit()

    # ── public ────────────────────────────────────────────────────────────────

    def get_params(self) -> dict:
        vcodec_data = self._vcodec_combo.currentData()
        vcodec = vcodec_data if vcodec_data else self._vcodec_combo.currentText()

        res = self._resolution_combo.currentText()
        if res == 'Custom':
            res = self._resolution_input.text().strip() or 'Original'

        fps = self._framerate_combo.currentText()
        if fps == 'Custom':
            fps = self._framerate_input.text().strip() or 'Original'

        return {
            'format':     self._fmt_combo.currentText(),
            'vcodec':     vcodec,
            'acodec':     self._acodec_combo.currentText(),
            'resolution': res,
            'framerate':  fps,
            'vbitrate':   self._vbitrate_combo.currentText(),
            'abitrate':   self._abitrate_combo.currentText(),
            'samplerate': self._samplerate_combo.currentText(),
            'channels':   self._channels_combo.currentText(),
        }
