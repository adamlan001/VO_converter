from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal


class ProgressItem(QFrame):
    cancel_requested = pyqtSignal()

    def __init__(self, filename: str):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self._label = QLabel(filename)
        self._label.setFixedWidth(200)
        self._label.setToolTip(filename)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(True)
        self._bar.setFormat('%p%')

        self._status = QLabel('Pending')
        self._status.setFixedWidth(80)

        self._btn = QPushButton('Cancel')
        self._btn.setFixedWidth(56)
        self._btn.clicked.connect(self.cancel_requested.emit)

        layout.addWidget(self._label)
        layout.addWidget(self._bar, 1)
        layout.addWidget(self._status)
        layout.addWidget(self._btn)

    def set_running(self):
        self._status.setText('Converting...')
        self._bar.setStyleSheet('')

    def set_progress(self, value: float):
        self._bar.setValue(int(value * 100))

    def set_finished(self, success: bool, msg: str):
        self._btn.setEnabled(False)
        if success:
            self._bar.setValue(100)
            self._status.setText('Done ✓')
            self._bar.setStyleSheet('QProgressBar::chunk { background-color: #4CAF50; }')
        else:
            self._status.setText('Cancelled' if msg == 'Cancelled' else 'Failed')
            self._status.setToolTip(msg)
            color = '#9E9E9E' if msg == 'Cancelled' else '#f44336'
            self._bar.setStyleSheet(f'QProgressBar::chunk {{ background-color: {color}; }}')


class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._vbox = QVBoxLayout(self._container)
        self._vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._vbox.setSpacing(3)
        scroll.setWidget(self._container)
        layout.addWidget(scroll)

        self._items: dict[str, ProgressItem] = {}

    def add_item(self, filename: str) -> ProgressItem:
        item = ProgressItem(filename)
        self._vbox.addWidget(item)
        self._items[filename] = item
        return item

    def get_item(self, filename: str) -> 'ProgressItem | None':
        return self._items.get(filename)

    def clear(self):
        for item in self._items.values():
            item.deleteLater()
        self._items.clear()
