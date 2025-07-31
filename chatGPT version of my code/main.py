# main.py

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
import sys
import PyQt6.QtMultimedia as QTM
from AudioSystem_PyQt6 import AudioManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AudioManager Demo")
        self.resize(300, 150)

        self.device = QTM.QMediaDevices.audioOutputs()[0]
        self.audio = AudioManager(self.device, volume=40)

        # Load test audio files
        self.audio.load("effect", "./startup.wav")  # Replace with actual file paths
        self.audio.load("music", "./startup.wav")

        layout = QVBoxLayout()
        playEffect = QPushButton("Play Sound Effect")
        playEffect.clicked.connect(lambda: self.audio.playSound("effect"))

        playMusic = QPushButton("Play Music (loop)")
        playMusic.clicked.connect(lambda: self.audio.playMusic("music", loop=True))

        stopAll = QPushButton("Stop All")
        stopAll.clicked.connect(self.audio.cleanup)

        layout.addWidget(playEffect)
        layout.addWidget(playMusic)
        layout.addWidget(stopAll)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.monitor = QTimer(self)
        self.monitor.timeout.connect(self.audioStatus)
        self.monitor.start(1000)

    def audioStatus(self):
        print("---")
        print("Sound Pool:", self.audio.pool["sound"])
        print("Music Pool:", self.audio.pool["music"])

    def closeEvent(self, event):
        print("[MainWindow] Cleaning up audio...")
        self.audio.cleanup()
        self.monitor.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
