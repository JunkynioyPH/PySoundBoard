import PyQt6.QtMultimedia as QtM # Perhaps a new Backend..?
from PyQt6.QtCore import QUrl
import time, xpfpath, os

class AudioMedia(QtM.QMediaPlayer):
    ...
class SoundEffect(QtM.QSoundEffect):
    def __init__(self, filePath:str):
        super().__init__()
        self.fileName:str = os.path.basename(filePath)
        self.filePath:str = xpfpath.xpfp(filePath)
        self.loopState:int = 0
        self.device:QtM.QAudioDevice = None
        
        self.setSource(QUrl.fromLocalFile(self.filePath)) # set sound file
    def setDevice(self, device:QtM.QAudioDevice):
        self.setAudioDevice(device)
    def setLoopState(self, state):
        self.loopState = state
    def setVol(self, vol):
        self.setVolume(vol) # ???????????????
    def playSound(self):
        self.setSource(QUrl.fromLocalFile(self.filePath)) # set sound file
        self.setLoopCount(((2**32)/2)-1 if self.loopState == 1 else 0) # set loop count NOT YET WORKING
        self.play() # play sound
        print(f"playing {self.filePath}")
            
class Audio():
# {"AudioName":QSoundEffect_OBJ}
    def __init__(self, device:QtM.QAudioDevice):
        self.loadedAudioFiles:list[SoundEffect|AudioMedia] = []
        self.device:QtM.QAudioDevice = device
        
    def setSfxVol(self, vol:int):
        for audio in self.loadedAudioFiles:
            audio.setVol(vol)
    def setAudioDevice(self, device:QtM.QAudioDevice):
        for audio in self.loadedAudioFiles:
            audio.setDevice(device)
    def loadSfx(self, file:str, vol:int=100):
        _ = SoundEffect(file)
        _.setAudioDevice(self.device)
        _.setVol(vol)
        self.loadedAudioFiles.append(_)
        print(self.loadedAudioFiles)
        
    
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
            
            self.device = QtM.QMediaDevices.audioOutputs()[0]
            Sound = Audio(self.device)
            Sound.loadSfx('./startup.wav')
            HBox.addWidget(FuncButton('Sound',Sound.loadedAudioFiles[0].play))
            # HBox.addWidget(FuncButton('Audio',SoundEffect("./startup.wav", self.device).playSound))
    
    
    MainFrame = MainWindow()
    MainFrame.show()
    sys.exit(APP.exec())  # Start the Application Event Loop