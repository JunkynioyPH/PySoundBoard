import PyQt6.QtMultimedia as QTM
from PyQt6.QtCore import QUrl, QTimer
import time, xpfpath, os

### Insert Main Code Here
class AudioManager():
    """
    Main Class which holds:
    
    - **loadedAudioFiles** & **audioPool**: _SoundEffect_|_AudioMedia_
    - **device**: _QAudioDevice_
    - **volume**: _int_ (_volume:int/100_)
    """
    def __init__(self, device:QTM.QAudioDevice, volume:int):
        """_summary_

        Args:
            device (QTM.QAudioDevice): _description_
            volume (int): _description_
        """
        self.device = device
        self.volume = volume
        self.loadedAudio:dict[dict] = {"audio":{},"sound":{}}
        self.audioPool:dict[list] = {"audio":[],"sound":[]}
    def infoMonitor(self):
        print(f"Supported MIME Types: {QTM.QSoundEffect.supportedMimeTypes()}")
        print(f"Loaded    : {self.loadedAudio}\nPlayerPool: {self.audioPool}")
    def loadSound(self, file:str):
        # use ./file.wav if ./ already exists, else append ./ prefix
        sound = xpfpath.xpfp(file) if xpfpath.xpfp('./') in file else xpfpath.xpfp(f"./{file}")
        # omit file extension
        soundName = os.path.splitext(os.path.basename(sound))[0]
        # on Key soundName, add value SoundEffectLoader
        self.loadedAudio["sound"][soundName] = sound
    def playSound(self, name:str, loop:bool=False):
        # get ./file
        path = self.loadedAudio["sound"].get(name)
        if not path:
            print(f"[AudioManager] Sound '{name}' not found.")
            return
        # create new SoundEffectPlayer(QSoundEffect) Instance with data from SoundEffectLoader
        loops = int(((2**32)/2)-1) if loop else 1
        player = SoundEffectPlayer(path, self.device, self.volume, loops)
        self.audioPool['sound'].append(player)
        player.play()
        player.playingChanged.connect(lambda: self._cleanupPlayer(player))
    def _cleanupPlayer(self, player):
        if not player.isPlaying():
            try:
                self.audioPool['sound'].remove(player)
            except ValueError:
                pass
class SoundEffectPlayer(QTM.QSoundEffect):
    def __init__(self, file:str, device:QTM.QAudioDevice, volume:int, loops:int):
        super().__init__()
        self.name = os.path.basename(file)
        self.setSource(QUrl.fromLocalFile(file))
        self.setAudioDevice(device)
        self.setVolume(volume/100)
        self.setLoopCount(loops)
    def __repr__(self) -> str:
        return self.name
        

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
            # self.method = Method # keep alive
            self.clicked.connect(Method)
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            Canvas = QWidget()

            HBox = QHBoxLayout()
            self.setCentralWidget(Canvas)
            Canvas.setLayout(HBox)
            
            self.device = QTM.QMediaDevices.audioOutputs()[0] # simulate loading prefered audioDevice
            sound = AudioManager(self.device,14) # init AudioSystem
            
            sound.loadSound('./startup.wav') # load Audio
            
            ## monitor sound list
            timer = QTimer(self)
            timer.timeout.connect(sound.infoMonitor)
            timer.start(500)
            
            # learned lambda
            HBox.addWidget(FuncButton('Sound', lambda play: sound.playSound('startup')))
    
    MainFrame = MainWindow()
    MainFrame.show()
    sys.exit(APP.exec())  # Start the Application Event Loop