from PyQt6.QtCore import Qt, QTimer, QSize, QUrl
from PyQt6.QtGui import QPixmap, QRegion # MAYBE ill get to work this at some point lmao
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import *
import json, os, sys, rich, darkmode
# from os import environ
# environ["QT_FFMPEG_LOG_LEVEL"] = "fatal"
# environ["QT_LOGGING_RULES"] = "*.debug=false;qt.multimedia.*=false"
APP = QApplication([])
import Soundboard_Backend_PyQt6 as SoundBackend
from rich import pretty
pretty.install()

# Initialise Instance of QApp
_ = QMediaDevices.audioOutputs() # Moving the FFMPEG thing
del _
# Load Settings
SoundBackend.InitializeSettings()
Settings = SoundBackend.Settings

if not Settings['UseSystemTheme']:
    APP.setStyle('Fusion')
    APP.setPalette(darkmode.get_slate_blue_dark_palette())
    rich.print('[PySoundboard] Using Built-in Dark Theme')
    
else:
    rich.print('[PySoundboard] Using System Theme')
    
# Console splash
def splash():
    # os.system('cls' if os.name=='nt' else 'clear')
    os.system('title PySoundBoard Backend') if os.name=='nt' else rich.print('\nPySoundBoard Backend')
    rich.print('''

    ██████╗ ██╗   ██╗███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██████╗  ██████╗  █████╗ ██████╗ ██████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
    ██████╔╝ ╚████╔╝ ███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║ Q
    ██╔═══╝   ╚██╔╝  ╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║ T
    ██║        ██║   ███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
                        Written By : @Junkynioy - https://github.com/JunkynioyPH
    ''')

def ShowSettings():
    rich.print("[PySoundboard] ", end='')
    for i in Settings:
        rich.print(f"[yellow][{i}:{Settings[i]}][/yellow] ", end='')
    else:
        rich.print()

def UpdateSettings(Variable,Value):
    rich.print(f"[PySoundboard] [green]Update Setting:[/green] <{Variable}> to '{Value}'")
    Settings[Variable] = Value
    with open("Settings.json","w") as UpdateSettings:
        UpdateSettings.write(json.dumps(Settings))
    SoundBackend.InitializeSettings() # Reload Settings
    ShowSettings()

# Show First-Time Execution then turn off pop up
# need to replace
if Settings["Splash"] == True:
    # os.system('python Splash.py')
    rich.print('='*20)
    UpdateSettings("Splash",False)

## Define Main Window
AlignFlag = Qt.AlignmentFlag
class updateTimerQueue(QTimer):
    def __init__(self, parent=None, ticks:int|None=None):
        super().__init__(parent)
        self.updateList:list = []
        self.timeout.connect(self.update)
        self.start(ticks) if ticks else self.start(250)
    
    def update(self):
        # rich.print(f'[PySoundboard] UpdaterTimerQueue {self.interval()}ms Elapsed')
        for item in self.updateList:
            item()
        # else:
        #     rich.print('[PySoundboard] UpdateTimerQueue: Update Finished')
    
    def appendToQueue(self, _callable):
        if not callable(_callable):
            return rich.print(f'[PySoundboard] UpdateTimerQueue: [red]Not Callable [/red]{_callable}')
        self.updateList.append(_callable)
        
    def popQueueItem(self, index:int):
        self.updateList.pop(index)
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.updaterLoop = updateTimerQueue(self)
        self.updaterLoop.appendToQueue(self.updateTopBarTitle)
        
        # Set adressable space
        BaseCanvas = QWidget()
        self.setCentralWidget(BaseCanvas)
        
        # Main adressable space
        VerticalCanvas = QVBoxLayout()
        
    def updateTopBarTitle(self):
        pass
        

# Generic Button which allows for 
# Text and .clicked.connect() declaration
# on the same line
class FuncButton(QPushButton):
    def __init__(self, Name:str, Method, width=125):
        super().__init__()
        # self.Method = Method
        self.setText(Name)
        self.setStyleSheet("text-align: left; padding: 5%; margin: 0%;")
        self.setFixedWidth(width)
        self.clicked.connect(Method)

# Initialize Backend
splash()
AudioSystem = SoundBackend.InitializeAudioSystem()
AudioSystem.togglePoolRollOver('audio')
buttonIndex = SoundBackend.GenerateSoundIndex(AudioSystem, SoundBackend.AudioFolder)
ShowSettings()
# Start Window
Main = MainWindow()
Main.show()
# SoundBackend.AudioSystem.status()
AudioSystem.addIndex(SoundBackend.SoundType.AUDIO_MEDIA,'./boop.wav')
AudioSystem.addIndex(SoundBackend.SoundType.AUDIO_MEDIA,'./startup.wav')

# try to look for a way to make this not be bound to only .wav files for startup sound!
# ^^^ In a way, this is already done.
# ^^^ Because  im using keyNames in Dicts now, which doesnt have file extensions.
AudioSystem.loadAudioMedia('audio','startup',0)
AudioSystem.playSlot('audio',0)

sys.exit(APP.exec())