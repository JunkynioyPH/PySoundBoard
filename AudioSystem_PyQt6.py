from PyQt6.QtMultimedia import *
from PyQt6.QtCore import QUrl, QTimer
from xpfpath import xpfp
import time, os


# main
class AudioManager():
    def __init__(self, device:QAudioDevice, volume:int=50):
        print(f"\nSupported MIME Types [QSoundEffect]:\n{QSoundEffect.supportedMimeTypes()}\n\nDetected AudioOutputs:\n{[Device.description() for Device in QMediaDevices.audioOutputs()]}\n")
        self.settings:dict[str:QAudioDevice, str:int] = {"device":device,"volume":volume}
        
        self.audioPool:dict[str:list, str:list] = {'audio':[],'sound':[]}
        self.audioIndex:dict[dict] = {'audio':{},'sound':{}}
        
    def status(self, terminal:bool=True) -> None|str:
        """Prints out the current Status of AudioManager"""
        status:str = f"...Index..:\n   Audio: {self.audioIndex['audio']}\n   Sound: {self.audioIndex['sound']}\n\nAudioPool.:\n   Audio: {self.audioPool['audio']}\n   Sound: {self.audioPool['sound']}"
        if terminal:
            print('++ [AudioManager] ++')
            print(status)
            print('++ -------------- ++')
        else:
            return status
    
    def load(self, type:str, path:str):
        audioName:str = os.path.splitext(os.path.basename(path))[0]
        print(f"[AudioManager] Load: ({type}) '{audioName}' <{path}> ", end='')
        
        ## Normalise path to have ' ./ , .\\ ' prefix
        ## In windows, this check will fail and duplicate " .\\ "
        ## However, " .\\.\\ " will still point to "Current Directory"
        ## I Should probably use "os.path" stuff for this instead of xpfp() shit thing i made
        path = path if xpfp('./') in path else xpfp(f'./{path}')
        
        # Check if type exist in the list
        if type.lower() != 'audio' and type.lower() != 'sound':
            return print("*Unknown Type*")
        # Check if key exist in dict, say it's a duplicate if it is
        if  self.audioIndex[type.lower()].get(audioName):
            return print(f'*Duplicate*')
        
        # else, make key
        if type.lower() == 'audio':
            self.audioIndex['audio'][audioName] = path
            print(f"*Loaded*")
        else:
            self.audioIndex['sound'][audioName] = path
            print(f"*Loaded*")
                
    def unload(self, type:str, item:str):
        print(f"[AudioManager] Unload: ({type}) <{item}> ", end='')
        # Check if type exist in the list
        if type.lower() != 'audio' and type.lower() != 'sound':
            return print("*Unknown Type*")
        # If it exists, ever. if not reply already unloaded
        if not self.audioIndex.get(type.lower()) and not self.audioIndex[type.lower()].get(item):
            return print(f"*Already Unloaded*")

        # else, unload
        if type.lower() == 'audio':
            self.audioIndex['audio'].pop(item)
            print(f"*Unloaded*")
        else:
            self.audioIndex['sound'].pop(item)
            print(f"*Unloaded*")


# remember when playing Audio/Sound, for "loops", pass in "### int(((2**32) / 2) - 1) if loop else 1 ###"
class SoundEffect(QSoundEffect):
    def __init__(self, file:str, device:QAudioDevice, volume:int, loops:int):
        super().__init__()
        self.name = os.path.basename(file)
        self.setAudioDevice(device)
        self.setSource(QUrl.fromLocalFile(file))
        
        self.setVolume(volume/100)
        self.setLoopCount(loops)
    def __repr__(self) -> str:
        return self.name

class AudioMedia(QMediaPlayer):
    def __init__(self, file:str, device:QAudioDevice, volume:int, loops:int):
        super().__init__()
        self.name = os.path.basename(file)
        self.device = QAudioOutput(device)
        self.setAudioOutput(self.device)
        self.setSource(QUrl.fromLocalFile(file))
        
        self.device.setVolume(volume/100)
        self.setLoops(loops)
    def __repr__(self) -> str:
        return self.name

# test

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
            
            self.device = QMediaDevices.audioOutputs()[0] # simulate loading prefered audioDevice
            self.sound = AudioManager(self.device,14) # init AudioSystem
            
            self.sound.load('sound','startup.wav')     # load sound
            self.sound.load('audio','startup.wav')     # load audio
            self.sound.load('vibration','startup.wav') # load unknown
            
            self.sound.unload('sound','startup')  # unload
            self.sound.unload('sound','startup')  # already unloaded
            self.sound.unload('sounds','startup') # invalid type
            
            self.sound.unload('audio','startup')   # unload
            self.sound.unload('audio','startup')   # already unloaded
            self.sound.unload('audios','startup')  # invalid type
            
            self.sound.load('sound','./startup.wav')     # load sound ./
            self.sound.load('audio','./startup.wav')     # load audio ./
            
            self.sound.load('audio','./SoundFiles/bonk.mp3') # load sound from nested folders
            self.sound.load('audio','SoundFiles/bonk.mp3')
            
            ## monitor sound list
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.sound.status)
            self.timer.start(500)
            
            # learned lambda
            HBox.addWidget(FuncButton('Sound', lambda: self.sound.playSound('startup')))
    
    MainFrame = MainWindow()
    MainFrame.show()
    sys.exit(APP.exec())  # Start the Application Event Loop