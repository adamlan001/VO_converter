import os
import subprocess
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QPushButton, QLineEdit, QFileDialog,
    QSpinBox, QMessageBox, QTextEdit, QDialog, QScrollArea,
)
from PyQt6.QtCore import Qt

from ui.file_list_widget import FileListWidget
from ui.format_panel import FormatPanel
from ui.progress_widget import ProgressWidget
from core.worker import ConversionWorker
from core.presets import FORMAT_CONFIG
from core import hw_detect


def _no_window():
    return subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


class LogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Conversion Log')
        self.resize(700, 400)
        layout = QVBoxLayout(self)
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setFontFamily('Consolas')
        layout.addWidget(self._text)

    def append(self, line: str):
        self._text.append(line)
        self._text.verticalScrollBar().setValue(self._text.verticalScrollBar().maximum())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VO Converter')
        self.resize(1050, 720)
        self._workers: dict[str, ConversionWorker] = {}
        self._queue: list[str] = []
        self._active_count = 0
        self._log_dialog = LogDialog(self)
        hw_encoders = hw_detect.detect()
        self._setup_ui(hw_encoders)
        self._check_ffmpeg(hw_encoders)

    # ── UI setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self, hw_encoders: set[str]):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(6)

        # Output dir row
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel('Output Dir:'))
        self._out_dir = QLineEdit()
        self._out_dir.setPlaceholderText('Leave empty to output to source directory')
        dir_row.addWidget(self._out_dir, 1)
        browse_btn = QPushButton('Browse...')
        browse_btn.setFixedWidth(70)
        browse_btn.clicked.connect(self._browse_out_dir)
        dir_row.addWidget(browse_btn)
        dir_row.addSpacing(12)
        dir_row.addWidget(QLabel('Concurrent:'))
        self._concurrent_spin = QSpinBox()
        self._concurrent_spin.setRange(1, 8)
        self._concurrent_spin.setValue(2)
        self._concurrent_spin.setFixedWidth(50)
        dir_row.addWidget(self._concurrent_spin)
        root.addLayout(dir_row)

        # Filename pattern row
        pattern_row = QHBoxLayout()
        pattern_row.addWidget(QLabel('Filename Pattern:'))
        self._pattern = QLineEdit()
        self._pattern.setText('{name}_converted')
        self._pattern.setPlaceholderText('{name}, {ext}, {format}, {timestamp}')
        self._pattern.setToolTip('Variables: {name}=original name, {ext}=extension, {format}=output format, {timestamp}=YYYYMMDD-HHMMSS')
        pattern_row.addWidget(self._pattern, 1)
        root.addLayout(pattern_row)

        # Main splitter: file list | format panel
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_box = QGroupBox('Source Files')
        ll = QVBoxLayout(left_box)
        ll.setContentsMargins(6, 6, 6, 6)
        self._file_list = FileListWidget()
        ll.addWidget(self._file_list)
        splitter.addWidget(left_box)

        right_box = QGroupBox('Settings')
        rl = QVBoxLayout(right_box)
        rl.setContentsMargins(6, 6, 6, 6)
        self._format_panel = FormatPanel(hw_encoders)

        # Wrap FormatPanel in scrollable area
        scroll = QScrollArea()
        scroll.setWidget(self._format_panel)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        rl.addWidget(scroll)
        splitter.addWidget(right_box)

        splitter.setSizes([640, 380])
        root.addWidget(splitter, 1)

        # Progress area
        prog_box = QGroupBox('Progress')
        pl = QVBoxLayout(prog_box)
        pl.setContentsMargins(6, 6, 6, 6)
        self._progress_widget = ProgressWidget()
        self._progress_widget.setMinimumHeight(80)
        pl.addWidget(self._progress_widget)
        root.addWidget(prog_box)

        # Bottom buttons
        btn_row = QHBoxLayout()
        log_btn = QPushButton('Show Log')
        log_btn.clicked.connect(self._log_dialog.show)
        btn_row.addWidget(log_btn)
        btn_row.addStretch()
        self._start_btn = QPushButton('Start')
        self._start_btn.setFixedHeight(36)
        self._start_btn.setStyleSheet(
            'QPushButton { background:#2196F3; color:white; font-weight:bold;'
            ' border-radius:4px; padding:0 24px; }'
            'QPushButton:disabled { background:#90CAF9; }'
        )
        self._start_btn.clicked.connect(self._start_conversion)
        self._cancel_btn = QPushButton('Cancel All')
        self._cancel_btn.setFixedHeight(36)
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self._cancel_all)
        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._cancel_btn)
        root.addLayout(btn_row)

        self.statusBar().showMessage('Ready')

    # ── ffmpeg check ──────────────────────────────────────────────────────────

    def _check_ffmpeg(self, hw_encoders: set[str]):
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True, timeout=10,
                creationflags=_no_window(),
            )
            gpu_info = hw_detect.brand_summary(hw_encoders)
            status = f'Ready  |  GPU: {gpu_info}' if gpu_info else 'Ready  |  GPU: Not detected (CPU encoding)'
            self.statusBar().showMessage(status)
        except FileNotFoundError:
            QMessageBox.warning(
                self, 'ffmpeg Not Found',
                'ffmpeg was not detected.\n\nPlease download it from https://ffmpeg.org/download.html '
                'and add it to your system PATH, then restart.',
            )

    # ── slots ─────────────────────────────────────────────────────────────────

    def _browse_out_dir(self):
        d = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if d:
            self._out_dir.setText(d)

    def _generate_output_filename(self, input_path: str, output_format: str) -> str:
        """Apply filename pattern to generate output filename."""
        pattern = self._pattern.text().strip() or '{name}_converted'
        stem = Path(input_path).stem
        orig_ext = Path(input_path).suffix.lstrip('.')
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

        result = pattern.format(
            name=stem,
            ext=orig_ext,
            format=output_format,
            timestamp=timestamp,
        )
        return result

    def _start_conversion(self):
        files = self._file_list.get_files()
        if not files:
            QMessageBox.warning(self, 'Warning', 'Please add source files first.')
            return

        params = self._format_panel.get_params()
        ext = FORMAT_CONFIG[params['format']]['ext']
        out_base = self._out_dir.text().strip()

        self._progress_widget.clear()
        self._workers.clear()
        self._queue.clear()
        self._active_count = 0
        self._start_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self.statusBar().showMessage(f'Preparing {len(files)} file(s)…')

        for fp in files:
            fname = os.path.basename(fp)
            out_dir = out_base if out_base else os.path.dirname(fp)
            out_filename = self._generate_output_filename(fp, params['format'])
            out_path = os.path.join(out_dir, f'{out_filename}.{ext}')

            item = self._progress_widget.add_item(fname)
            worker = ConversionWorker(fp, out_path, params)

            def _make_cb(fn, it):
                def on_progress(v):    it.set_progress(v)
                def on_log(line):      self._log_dialog.append(line)
                def on_finished(ok, msg):
                    it.set_finished(ok, msg)
                    self._on_done(fn)
                return on_progress, on_log, on_finished

            on_p, on_l, on_f = _make_cb(fname, item)
            worker.progress.connect(on_p)
            worker.log_line.connect(on_l)
            worker.finished.connect(on_f)
            item.cancel_requested.connect(lambda fn=fname: self._cancel_one(fn))

            self._workers[fname] = worker
            self._queue.append(fname)

        self._dispatch()

    def _dispatch(self):
        limit = self._concurrent_spin.value()
        while self._active_count < limit and self._queue:
            fname = self._queue.pop(0)
            worker = self._workers.get(fname)
            if worker:
                item = self._progress_widget.get_item(fname)
                if item:
                    item.set_running()
                worker.start()
                self._active_count += 1

    def _on_done(self, fname: str):
        self._active_count -= 1
        if self._queue:
            self._dispatch()
        elif self._active_count == 0:
            self._start_btn.setEnabled(True)
            self._cancel_btn.setEnabled(False)
            self.statusBar().showMessage('All done')

    def _cancel_one(self, fname: str):
        if fname in self._queue:
            self._queue.remove(fname)
            item = self._progress_widget.get_item(fname)
            if item:
                item.set_finished(False, 'Cancelled')
            return
        worker = self._workers.get(fname)
        if worker and worker.isRunning():
            worker.cancel()

    def _cancel_all(self):
        self._queue.clear()
        for worker in self._workers.values():
            if worker.isRunning():
                worker.cancel()

    def closeEvent(self, event):
        self._cancel_all()
        for worker in self._workers.values():
            worker.wait(3000)
        event.accept()
