import sys
import time

import libtorrent as lt
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QProgressBar


class BitTorrentClient(QWidget):
    def __init__(self):
        super().__init__()

        # init client session and listen on ports for peers
        self.session = lt.session()
        self.session.listen_on(6881, 6891)

        # init pyqt user interface
        self.torrent_path_label = QLabel("Torrent path:")
        self.torrent_path_edit = QLineEdit()
        self.download_button = QPushButton("Download")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.success_label = QLabel("")

        # map download button to relevant method
        self.download_button.clicked.connect(self.download)

        # add pyqt widgets to layout
        layout = QVBoxLayout()
        layout.addWidget(self.torrent_path_label)
        layout.addWidget(self.torrent_path_edit)
        layout.addWidget(self.download_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.success_label)
        self.setLayout(layout)

        # init windows app properties
        self.setWindowTitle("storrent")
        self.show()

    def download(self):
        # .torrent path from ui text field
        pth = self.torrent_path_edit.text()
        magnet_info = lt.torrent_info(pth)

        # add torrent to the session
        conn = self.session.add_torrent({'ti': magnet_info, 'save_path': './storrent_downloads'})

        # download the file and update the ui's progress bar
        while not conn.is_seed():
            s = conn.status()
            self.progress_bar.setValue(s.progress * 100)
            time.sleep(1)

        self.progress_bar.setVisible(False)
        self.success_label.setText("Download complete!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = BitTorrentClient()
    sys.exit(app.exec_())
