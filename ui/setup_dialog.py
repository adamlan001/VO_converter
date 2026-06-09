import io
import os
import urllib.request
import zipfile

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QProgressBar, QPushButton, QVBoxLayout,
)

from core.ffmpeg_resolver import _app_dir

FFMPEG_ZIP_URL = (
    'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/'
    'ffmpeg-master-latest-win64-gpl-shared.zip'
)


class _DownloadThread(QThread):
    progress = pyqtSignal(int)      # 0-100
    status = pyqtSignal(str)
    succeeded = pyqtSignal()
    failed = pyqtSignal(str)

    def run(self):
        bin_dir = os.path.join(_app_dir(), 'bin')
        os.makedirs(bin_dir, exist_ok=True)

        try:
            self.status.emit('正在連線到 GitHub …')
            req = urllib.request.Request(
                FFMPEG_ZIP_URL,
                headers={'User-Agent': 'VO-Converter/0.1'},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get('Content-Length', 0))
                self.status.emit('正在下載 ffmpeg …')
                buf = io.BytesIO()
                downloaded = 0
                chunk = 65536
                while True:
                    data = resp.read(chunk)
                    if not data:
                        break
                    buf.write(data)
                    downloaded += len(data)
                    if total:
                        self.progress.emit(int(downloaded / total * 90))

            self.status.emit('正在解壓縮 …')
            buf.seek(0)
            with zipfile.ZipFile(buf) as zf:
                for name in zf.namelist():
                    basename = os.path.basename(name)
                    if basename in ('ffmpeg.exe', 'ffprobe.exe'):
                        dest = os.path.join(bin_dir, basename)
                        with zf.open(name) as src, open(dest, 'wb') as dst:
                            dst.write(src.read())

            ffmpeg_ok = os.path.isfile(os.path.join(bin_dir, 'ffmpeg.exe'))
            ffprobe_ok = os.path.isfile(os.path.join(bin_dir, 'ffprobe.exe'))
            if not ffmpeg_ok or not ffprobe_ok:
                self.failed.emit('ZIP 中找不到 ffmpeg.exe / ffprobe.exe，請回報此問題。')
                return

            self.progress.emit(100)
            self.status.emit('完成！')
            self.succeeded.emit()

        except Exception as e:
            self.failed.emit(str(e))


class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('首次設定 — 下載 ffmpeg')
        self.setMinimumWidth(420)
        self.setModal(True)
        self._thread = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        info = QLabel(
            '<b>VO Converter</b> 需要 <b>ffmpeg</b> 才能轉換影音檔案。<br><br>'
            '點擊「下載 ffmpeg」，程式將自動從 GitHub 下載並安裝（約 70 MB）。<br>'
            '下載完成後即可開始使用，之後啟動無需重複下載。'
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self._status_label = QLabel('等待開始 …')
        layout.addWidget(self._status_label)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        self._btn_download = QPushButton('下載 ffmpeg')
        self._btn_download.clicked.connect(self._start_download)
        layout.addWidget(self._btn_download)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        buttons.rejected.connect(self.reject)
        self._btn_cancel = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

    def _start_download(self):
        self._btn_download.setEnabled(False)
        self._btn_cancel.setEnabled(False)
        self._thread = _DownloadThread(self)
        self._thread.progress.connect(self._progress.setValue)
        self._thread.status.connect(self._status_label.setText)
        self._thread.succeeded.connect(self._on_success)
        self._thread.failed.connect(self._on_failure)
        self._thread.start()

    def _on_success(self):
        self._btn_cancel.setEnabled(True)
        self._status_label.setText('ffmpeg 安裝完成，點擊「確定」繼續。')
        ok_btn = QPushButton('確定')
        ok_btn.clicked.connect(self.accept)
        self.layout().addWidget(ok_btn)

    def _on_failure(self, msg: str):
        self._btn_download.setEnabled(True)
        self._btn_cancel.setEnabled(True)
        self._status_label.setText(f'下載失敗：{msg}')
        self._progress.setValue(0)
