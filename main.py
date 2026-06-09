import sys
from PyQt6.QtWidgets import QApplication, QDialog
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('VO Converter')
    app.setStyle('Fusion')

    from core.ffmpeg_resolver import is_ffmpeg_available
    if not is_ffmpeg_available():
        from ui.setup_dialog import SetupDialog
        dlg = SetupDialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
