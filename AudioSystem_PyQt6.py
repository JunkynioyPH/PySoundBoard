import PyQt6.QtMultimedia as QTM
from PyQt6.QtCore import QUrl
import time, xpfpath, os

### Insert Main Code Here
print(...)

### Practical Tests
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QPushButton
    import sys
    from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget
    
    APP = QApplication([])
    class FuncButton(QPushButton):
        def __init__(self, Name:str, Method:classmethod):
            super().__init__()
            self.setText(Name)
            self.setStyleSheet("text-align: left; padding: 5%; margin: 0%;")
            self.setFixedWidth(125)
            self.method = Method # keep CLASS INSTANCE alive
            self.clicked.connect(self.method)
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            Canvas = QWidget()

            HBox = QHBoxLayout()
            self.setCentralWidget(Canvas)
            Canvas.setLayout(HBox)
            
            # self.device = QtM.QMediaDevices.audioOutputs()[0]
            # Sound = Audio(self.device)
            # Sound.loadSfx('./startup.wav')
            HBox.addWidget(FuncButton('Sound',print))
            # HBox.addWidget(FuncButton('Sound',Sound.loadedAudioFiles[0].play))
            # HBox.addWidget(FuncButton('Audio',SoundEffect("./startup.wav", self.device).playSound))
    
    
    MainFrame = MainWindow()
    MainFrame.show()
    sys.exit(APP.exec())  # Start the Application Event Loop