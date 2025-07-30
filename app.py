import sys
import subprocess
import signal
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QTimer

RADIOS = {
    "Radio Impuls": "https://live.radio-impuls.ro/stream",
    "DanceFM": "https://edge126.rcs-rds.ro/profm/dancefm.mp3",
    "Virgin Radio": "https://astreaming.edi.ro:8443/VirginRadio_aac",
    "Radio Brașov": "https://live.radiobrasov.ro/stream.mp3",
    "Radio ZU": "https://live7digi.antenaplay.ro/radiozu/radiozu-48000.m3u8"
}

class VUMeter(QWidget):
    def __init__(self):
        super().__init__()
        self.level = 0
        self.setMinimumWidth(40)

    def setLevel(self, value):
        self.level = max(0, min(100, value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(self.rect())
        height = int(self.height() * (self.level / 100))
        color = Qt.green if self.level < 60 else Qt.yellow if self.level < 85 else Qt.red
        painter.setBrush(QBrush(color))
        painter.drawRect(5, self.height() - height, self.width()-10, height)

class RadioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radio Player by Adrian T")
        self.setGeometry(300, 200, 500, 300)
        self.setFixedSize(self.size()) 

        self.ffplay_process = None

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Times New Roman", 12))
        for station in RADIOS.keys():
            self.list_widget.addItem(station)
        self.list_widget.itemDoubleClicked.connect(self.play_selected)
        left_layout.addWidget(self.list_widget)

        self.status_label = QLabel("<span style='color:red; font-weight:bold;'>Selectează un radio</span>")

        self.status_label.setFont(QFont("Times New Roman", 12))
        left_layout.addWidget(self.status_label)

        self.play_btn = QPushButton("Play")
        self.play_btn.setFont(QFont("Times New Roman", 12))
        self.play_btn.clicked.connect(self.play_selected)
        left_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setFont(QFont("Times New Roman", 12))
        self.stop_btn.clicked.connect(self.stop_radio)
        left_layout.addWidget(self.stop_btn)

        self.copy_label = QLabel("© Adrian T")
        self.copy_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.copy_label.setFont(QFont("Times New Roman", 10))
        left_layout.addWidget(self.copy_label)

        self.vu = VUMeter()
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.vu)
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_vu)
        self.timer.start(100)

    def update_vu(self):
        if self.ffplay_process:
            self.vu.setLevel(random.randint(30, 100))
        else:
            self.vu.setLevel(0)

    def play_selected(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        station = selected_items[0].text()
        url = RADIOS[station]

        self.stop_radio()

        # Pornim ffplay fără fereastră
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.ffplay_process = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo
        )

        self.status_label.setText(
        f"<span style='color:green; font-weight:bold;'>🎶 Redă: {station}</span>"
    )
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setForeground(QColor("green") if item.text() == station else QColor("red"))
    def closeEvent(self, event):
        if self.ffplay_process:
              self.ffplay_process.kill()
        event.accept()

    def stop_radio(self):
        if self.ffplay_process:
            self.ffplay_process.send_signal(signal.SIGTERM)
            self.ffplay_process = None
        self.status_label.setText("<span style='color:red; font-weight:bold;'>⛔ Oprit</span>")
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setForeground(QColor("red"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RadioPlayer()
    window.show()
    sys.exit(app.exec_())
