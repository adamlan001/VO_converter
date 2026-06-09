import os
import subprocess
import threading
from PyQt6.QtCore import QThread, pyqtSignal
from core.converter import probe_duration, build_command


def _no_window():
    return subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


class ConversionWorker(QThread):
    progress = pyqtSignal(float)        # 0.0 – 1.0
    log_line = pyqtSignal(str)
    finished = pyqtSignal(bool, str)    # success, message

    def __init__(self, input_path: str, output_path: str, params: dict):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.params = params
        self._cancelled = False
        self._process = None

    def cancel(self):
        self._cancelled = True
        if self._process and self._process.poll() is None:
            self._process.terminate()

    def run(self):
        try:
            duration = probe_duration(self.input_path)
            cmd = build_command(self.input_path, self.output_path, self.params)
            self.log_line.emit(' '.join(f'"{a}"' if ' ' in a else a for a in cmd))

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=_no_window(),
            )

            # Drain stderr in background to prevent pipe-buffer deadlock
            stderr_lines: list[str] = []

            def _drain_stderr():
                for line in self._process.stderr:
                    stderr_lines.append(line)

            t = threading.Thread(target=_drain_stderr, daemon=True)
            t.start()

            for line in self._process.stdout:
                if self._cancelled:
                    break
                line = line.strip()
                if line.startswith('out_time_ms='):
                    try:
                        ms = int(line.split('=')[1])
                        if duration > 0:
                            pct = min(ms / 1_000_000 / duration, 1.0)
                            self.progress.emit(pct)
                    except ValueError:
                        pass

            self._process.wait()
            t.join(timeout=5)

            if self._cancelled:
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)
                self.finished.emit(False, 'Cancelled')
            elif self._process.returncode == 0:
                self.progress.emit(1.0)
                self.finished.emit(True, 'Done')
            else:
                err = ''.join(stderr_lines)
                self.finished.emit(False, err[-300:] if err else f'exit code {self._process.returncode}')

        except FileNotFoundError:
            self.finished.emit(False, 'ffmpeg not found. Please install it and add to PATH.')
        except Exception as e:
            self.finished.emit(False, str(e))
