import sys
import time
import json
import os
import libtorrent as lt
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
    QProgressBar, QFileDialog, QListWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

from plyer import notification
import subprocess

APP_DATA_DIR = Path(os.getenv("APPDATA", ".")) / "sTorrent"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = APP_DATA_DIR / "download_history.json"
DOWNLOAD_PATH = APP_DATA_DIR / "storrent_downloads"
DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)

class DownloadThread(QThread):
    progress = pyqtSignal(float)
    complete = pyqtSignal(str)
    paused = pyqtSignal(bool)
    cancelled = pyqtSignal()

    def __init__(self, session, torrent_path):
        super().__init__()
        self.session = session
        self.torrent_path = torrent_path
        self.conn = None
        self.is_paused = False
        self.is_cancelled = False

    def run(self):
        try:
            magnet_info = lt.torrent_info(self.torrent_path)
            self.conn = self.session.add_torrent({
                'ti': magnet_info,
                'save_path': str(DOWNLOAD_PATH)
            })

            while not self.conn.is_seed():
                if self.is_cancelled:
                    self.session.remove_torrent(self.conn)
                    self.cancelled.emit()
                    return

                if not self.is_paused:
                    s = self.conn.status()
                    self.progress.emit(s.progress * 100)

                time.sleep(1)

            self.complete.emit(self.conn.name())
        except Exception as e:
            print(f"Error: {e}")

    def pause(self):
        if self.conn:
            self.conn.pause()
            self.is_paused = True
            self.paused.emit(True)

    def resume(self):
        if self.conn:
            self.conn.resume()
            self.is_paused = False
            self.paused.emit(False)

    def cancel(self):
        self.is_cancelled = True


class BitTorrentClient(QWidget):
    def __init__(self):
        super().__init__()

        icon_path = str("favicon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.session = lt.session()
        self.session.listen_on(6881, 6891)

        # UI Elements
        self.torrent_path_label = QLabel("Torrent Path:")
        self.torrent_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.download_button = QPushButton("Download")
        self.pause_button = QPushButton("Pause")
        self.cancel_button = QPushButton("Cancel")
        self.progress_bar = QProgressBar()
        self.success_label = QLabel("")
        self.history_list = QListWidget()

        # Connect UI Elements
        self.browse_button.clicked.connect(self.browse_file)
        self.download_button.clicked.connect(self.start_download)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.cancel_button.clicked.connect(self.cancel_download)
        self.history_list.itemDoubleClicked.connect(self.open_directory)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.torrent_path_label)
        layout.addWidget(self.torrent_path_edit)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.download_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Download History:"))
        layout.addWidget(self.history_list)
        layout.addWidget(self.success_label)
        self.setLayout(layout)

        # Button States
        self.pause_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        # Window Properties
        self.setWindowTitle("sTorrent")
        self.load_download_history()
        self.show()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Torrent File", "", "Torrent Files (*.torrent)")
        if file_path:
            self.torrent_path_edit.setText(file_path)

    def start_download(self):
        torrent_path = self.torrent_path_edit.text().strip()
        if not torrent_path:
            self.success_label.setText("Please provide a valid torrent path.")
            return

        self.download_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.download_thread = DownloadThread(self.session, torrent_path)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.complete.connect(self.download_complete)
        self.download_thread.paused.connect(self.update_pause_status)
        self.download_thread.cancelled.connect(self.download_cancelled)
        self.download_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def download_complete(self, torrent_name):
        self.progress_bar.setVisible(False)
        self.success_label.setText(f"Download complete: {torrent_name}")
        self.save_download_history(torrent_name)
        notification.notify(
            title="Download Complete!",
            message=f"{torrent_name} has finished downloading.",
            timeout=10
        )
        self.reset_buttons()

    def toggle_pause(self):
        if self.download_thread.is_paused:
            self.download_thread.resume()
        else:
            self.download_thread.pause()

    def update_pause_status(self, is_paused):
        self.pause_button.setText("Resume" if is_paused else "Pause")

    def cancel_download(self):
        self.download_thread.cancel()

    def download_cancelled(self):
        self.success_label.setText("Download cancelled!")
        self.progress_bar.setValue(0)
        self.reset_buttons()

    def open_directory(self, item):
        torrent_name = item.text().split(" | ")[0]
        download_dir = DOWNLOAD_PATH / torrent_name

        if download_dir.exists():
            if sys.platform == "win32":
                os.startfile(download_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(download_dir)])
            else:
                subprocess.run(["xdg-open", str(download_dir)])
        else:
            QMessageBox.warning(self, "Error", "Directory not found.")

    def reset_buttons(self):
        self.download_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def load_download_history(self):
        if HISTORY_FILE.exists():
            with HISTORY_FILE.open("r") as f:
                history = json.load(f)
                for entry in history:
                    self.history_list.addItem(f"{entry['name']} | {entry['timestamp']}")

    def save_download_history(self, torrent_name):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {"name": torrent_name, "timestamp": timestamp}

        history = []
        if HISTORY_FILE.exists():
            with HISTORY_FILE.open("r") as f:
                history = json.load(f)
        history.append(entry)

        with HISTORY_FILE.open("w") as f:
            json.dump(history, f, indent=4)

        self.history_list.addItem(f"{torrent_name} | {timestamp}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_icon_path = str("favicon.ico")
    app.setWindowIcon(QIcon(app_icon_path))
    client = BitTorrentClient()
    sys.exit(app.exec_())
