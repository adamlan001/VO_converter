import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFileDialog, QLabel, QMenu,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent

SUPPORTED_EXTS = {
    '.mp4', '.mkv', '.mov', '.avi', '.webm', '.flv', '.wmv', '.m4v',
    '.mp3', '.aac', '.wav', '.flac', '.ogg', '.m4a', '.wma', '.opus',
}


class _DropTable(QTableWidget):
    """QTableWidget subclass with proper file drag & drop support."""
    files_dropped = pyqtSignal(list)
    delete_row = pyqtSignal(int)

    def __init__(self):
        super().__init__(0, 3)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        row = self.rowAt(pos.y())
        if row >= 0:
            menu = QMenu(self)
            menu.addAction('Remove').triggered.connect(lambda: self.delete_row.emit(row))
            menu.exec(self.mapToGlobal(pos))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            self.files_dropped.emit([url.toLocalFile() for url in event.mimeData().urls()])
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class FileListWidget(QWidget):
    files_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._files: list[str] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton('+ Add Files')
        self.add_btn.clicked.connect(self._add_files)
        self.clear_btn = QPushButton('Clear All')
        self.clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.table = _DropTable()
        self.table.setHorizontalHeaderLabels(['Filename', 'Size', 'Status'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.files_dropped.connect(self._on_dropped)
        self.table.delete_row.connect(self._delete_row)
        layout.addWidget(self.table)

        hint = QLabel('Drag & drop files here, or click "Add Files"')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet('color: gray; font-size: 11px; padding: 4px;')
        layout.addWidget(hint)

    def _on_dropped(self, paths: list):
        added = False
        for path in paths:
            if os.path.isfile(path):
                added |= self._add_file(path)
            elif os.path.isdir(path):
                for f in Path(path).rglob('*'):
                    if f.suffix.lower() in SUPPORTED_EXTS:
                        added |= self._add_file(str(f))
        if added:
            self.files_changed.emit()

    def get_files(self) -> list[str]:
        return list(self._files)

    def set_status(self, index: int, status: str):
        if 0 <= index < self.table.rowCount():
            self.table.item(index, 2).setText(status)

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, 'Select Media Files', '',
            'Media Files (*.mp4 *.mkv *.mov *.avi *.webm *.flv *.wmv *.m4v '
            '*.mp3 *.aac *.wav *.flac *.ogg *.m4a *.wma *.opus);;All Files (*)',
        )
        added = any(self._add_file(p) for p in paths)
        if added:
            self.files_changed.emit()

    def _add_file(self, path: str) -> bool:
        if path in self._files:
            return False
        self._files.append(path)
        row = self.table.rowCount()
        self.table.insertRow(row)
        name_item = QTableWidgetItem(os.path.basename(path))
        name_item.setToolTip(path)
        self.table.setItem(row, 0, name_item)
        self.table.setItem(row, 1, QTableWidgetItem(_fmt_size(os.path.getsize(path))))
        self.table.setItem(row, 2, QTableWidgetItem('Pending'))
        return True

    def _clear_all(self):
        self._files.clear()
        self.table.setRowCount(0)
        self.files_changed.emit()

    def _delete_row(self, row: int):
        if 0 <= row < len(self._files):
            self._files.pop(row)
            self.table.removeRow(row)
            self.files_changed.emit()


def _fmt_size(size: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size < 1024:
            return f'{size:.1f} {unit}'
        size /= 1024
    return f'{size:.1f} TB'
