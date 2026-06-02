from PyQt6.QtCore import Qt, QTimer, QSize, QUrl, QObject, QEvent
from PyQt6.QtGui import QPixmap, QRegion # MAYBE ill get to work this at some point lmao
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import *
import json, os, sys, rich
APP = QApplication([])
import Soundboard_Backend_PyQt6 as SoundBackend
from rich import pretty
pretty.install()

# Initialise Instance of QApp
_ = QMediaDevices.audioOutputs(); del _ # Moving the FFMPEG thing
# Load Settings
SoundBackend.InitializeSettings()
Settings = SoundBackend.Settings

if not Settings['UseSystemTheme']:
    import darkmode
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
    ██████╔╝ ╚████╔╝ ███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║
    ██╔═══╝   ╚██╔╝  ╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║
    ██║        ██║   ███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
                        Written By : @junkynioy - https://github.com/JunkynioyPH        PyQt6 RE: GUI_E.B.
    ''')

def ShowSettings():
    rich.print("[PySoundboard] ", end='')
    for i in Settings:
        rich.print(f"[yellow][{i}:{Settings[i]}][/yellow] ", end='')
    else:
        print()

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
        for item in self.updateList:
            item()
            
    def appendToQueue(self, _callable):
        rich.print('[PySoundboard] UpdateTimerQueue: ', end='')
        if not callable(_callable):
            return rich.print(f'[red]Not Callable [/red]{_callable}')
        rich.print(f'[green]Appended [/green] {_callable}')
        self.updateList.append(_callable)
        
    def popQueueItem(self, index:int):
        self.updateList.pop(index)

class sections:
    class SoundButtons(QGroupBox):
        def __init__(self, title, parent=None):
            super().__init__(title, parent)
    class SlotStatusMonitor(QGroupBox):
        def __init__(self, title, parent=None):
            super().__init__(title, parent)
    class AudioIndexMonitor(QGroupBox):
        def __init__(self, title, parent=None):
            super().__init__(title, parent)
    class PySoundboardSettings(QGroupBox):
        def __init__(self, title, parent=None):
            super().__init__(title, parent)

# Ai Assisted, Keyfilter code START
class ArrowKeysFilter_SaveVolume(QObject):
    def __init__(self, callback):
        super().__init__()
        if not callable(callback):
            raise TypeError(f"{callback} Not Calllable Method")
        self.callback = callback
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            match event.key():
                case Qt.Key.Key_Left | Qt.Key.Key_Right | Qt.Key.Key_Up | Qt.Key.Key_Down:
                    rich.print('[PySoundboard] KeyPress: <ARROW_KEY>')
                    self.callback()
        return False   
# Ai Assisted, Keyfilter code END

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.updaterLoop = updateTimerQueue(self)
        self.updaterLoop.appendToQueue(self._updateTopBarTitle)
        self.setWindowTitle('PySoundboard PyQt6 GUI')
#         self.setObjectName('baseCanvas')
#         ## To keep ASPECT_RATIO use:
#         # background-image: url(image.png);
#         self.setStyleSheet("""
#     QWidget#baseCanvas {
#         border-image: url(test.png) 0 0 0 0 stretch stretch;
#         background-position: center;
#         }
# """)
        # Set adressable space
        BaseCanvas = QWidget()
        self.setCentralWidget(BaseCanvas)
        
        # Main adressable space
        VerticalCanvas = QVBoxLayout()
        BaseCanvas.setLayout(VerticalCanvas)
        
        # GUI sections
        topBarCanvas = QHBoxLayout()
        self.topBarStatus = QLabel()
        topBarCanvas.addWidget(QLabel("PySoundboard PyQt6 - @junkynioy :"))
        topBarCanvas.addWidget(self.topBarStatus)
        self.topBarStatus.setAlignment(AlignFlag.AlignHCenter)
        
        self.audioDeviceControlsGroup = QGroupBox('')
        self.mediaControlsGroup = QGroupBox('')
        self.soundboardTabsGroup = QTabWidget()
        
        VerticalCanvas.addLayout(topBarCanvas)
        widgets = [
            self.audioDeviceControlsGroup,
            self.mediaControlsGroup,
            self.soundboardTabsGroup
        ]
        for widget in widgets:
            VerticalCanvas.addWidget(widget)
        else:
            self.bakeGroupContents()
        VerticalCanvas.addStretch(1)
        
    
    def bakeGroupContents(self):
        self._audioDeviceControlsContent()
        self._mediaControlsContent()
        self._soundboardTabsContent()
        
    def _updateTopBarTitle(self):
        name, src, mediastat, loopstat, playstat, playrate = AudioSystem.audioPool['audio'][SoundBackend.SelectedSlot].getStatus()
        _text = f'[Slot {name} - {mediastat if src == '' else src}{f" : {loopstat}" if loopstat != '' else ''}{f" : {mediastat}" if src != '' else ''} : {playstat} @ {playrate}x]'
        self.topBarStatus.setText(_text)
    
    def _audioDeviceControlsContent(self):
        audioDeviceCanvas = QHBoxLayout()
        self.audioDeviceControlsGroup.setLayout(audioDeviceCanvas)
        audioDeviceCanvas.addStretch(1)
        
        # Audio Device Select Combo Box START
        audioDeviceSelectCanvas = QVBoxLayout()
        self.audioDeviceSelectComboBox = QComboBox()
        audioDeviceSelectCanvas.addWidget(QLabel("Current Device:"))
        audioDeviceSelectCanvas.addWidget(self.audioDeviceSelectComboBox)
        def _changeDevice():
            def _getDevice():
                devices = QMediaDevices.audioOutputs()
                for device in devices:
                    if device.description() == self.audioDeviceSelectComboBox.currentText():
                        # rich.print(device, device.description(), self.audioDeviceSelectComboBox.currentText())
                        return device
            try:
                UpdateSettings("AudioDevice",self.audioDeviceSelectComboBox.currentText())
                AudioSystem.setDevice(_getDevice(), True)
                AudioSystem.loadAudioMedia('audio','startup',0)
                AudioSystem.playSlot('audio',0)
                splash()
                rich.print(f"[PySoundboard] <{f'Default Device"{Settings["AudioDevice"]}"' if Settings["AudioDevice"] is None else self.audioDeviceSelectComboBox.currentText()}> Found!\n[PySoundboard] Successfully Bound to Device!")
                
            except Exception as ERR:
                splash()
                rich.print('[PySoundboard] System Defaulting!')
                UpdateSettings("AudioDevice", None)
                AudioSystem.setDevice(QMediaDevices.defaultAudioOutput(), True)
                AudioSystem.loadAudioMedia('audio','startup',0)
                AudioSystem.playSlot('audio',0)
                rich.print(f"[PySoundboard] [{self.audioDeviceSelectComboBox.currentText()}] : {repr(ERR)}\n[PySoundboard] Restart Soundboard to refresh Dropdown List ") if self.audioDeviceSelectComboBox.currentIndex() != 0 else ''
                
        self.audioDeviceSelectComboBox.setFixedSize(370, 42)
        self.audioDeviceSelectComboBox.setPlaceholderText('Defaulting, Select an Output Device...')
        self.audioDeviceSelectComboBox.addItems([device.description() for device in QMediaDevices.audioOutputs()])
        self.audioDeviceSelectComboBox.setCurrentIndex(self.audioDeviceSelectComboBox.findText(Settings["AudioDevice"]))
        self.audioDeviceSelectComboBox.activated.connect(_changeDevice)
        audioDeviceCanvas.addLayout(audioDeviceSelectCanvas)
        # Audio Device Select Combo Box END
        # Audio Device Volume Control START
        def _changeVolume():
            Volume = int(self.audioDeviceVolumeSlider.value())
            self.audioDeviceVolumeLabel.setText(f"Volume: {Volume}%")
            AudioSystem.setVolume('audio', Volume)
        def _saveVolume():
            UpdateSettings("Volume", self.audioDeviceVolumeSlider.value())
        audioDeviceVolumeControlCanvas = QVBoxLayout()
        self.audioDeviceVolumeLabel = QLabel(f"Volume: {Settings.get('Volume')}%")
        audioDeviceVolumeControlCanvas.addWidget(self.audioDeviceVolumeLabel)
        self.audioDeviceVolumeSlider = QSlider(Qt.Orientation.Horizontal)
        self.audioDeviceVolumeSlider.setFixedSize(200,11)
        self.audioDeviceVolumeSlider.setRange(0, 100)
        audioDeviceVolumeControlCanvas.addWidget(self.audioDeviceVolumeSlider)
        self.audioDeviceVolumeSlider.setValue(int(Settings['Volume']))
        self.audioDeviceVolumeSlider.valueChanged.connect(_changeVolume)
        ### KeyFilter Event, Ai Assisted code START
        self.arrowKeys_saveVolume = ArrowKeysFilter_SaveVolume(_saveVolume)
        self.audioDeviceVolumeSlider.installEventFilter(self.arrowKeys_saveVolume)
        ### Keyfilter Event, Ai Assisted code END
        self.audioDeviceVolumeSlider.sliderReleased.connect(_saveVolume)
        audioDeviceCanvas.addLayout(audioDeviceVolumeControlCanvas)
        # Audio Device Volume Control END
        # Audio Device Global PlaybackSettings START
        ## TODO: ADD GLOBAL PLAYBACKSPEED SLIDER
        audioDevicePlaySpeedCanvas = audioDeviceVolumeControlCanvas
        def _changeSpeed():
            self.audioDeviceSpeedLabel.setText(f"Playback Speed: x{self.audioDeviceSpeedSlider.value()/100}")
        
        self.audioDeviceSpeedSlider = QSlider(Qt.Orientation.Horizontal)
        self.audioDeviceSpeedLabel = QLabel('Playback Speed: x1.0')
        audioDevicePlaySpeedCanvas.addWidget(self.audioDeviceSpeedLabel)
        audioDevicePlaySpeedCanvas.addWidget(self.audioDeviceSpeedSlider)
        # self.audioDeviceSpeedSlider.setFixedWidth(200)
        self.audioDeviceSpeedSlider.setFixedSize(200,11)
        
        self.audioDeviceSpeedSlider.setRange(0, 500)
        self.audioDeviceSpeedSlider.setValue(100)
        # better test some point whether if it's better to apply real-time or after released
        self.audioDeviceSpeedSlider.valueChanged.connect(_changeSpeed)
        # self.audioDeviceSpeedSlider.sliderReleased.connect(_changeSpeed)
        
        
        audioDeviceToggles = QVBoxLayout()
        def _toggleGlobalLoopMod():
            print('GLOBAL LOOP TOGGLE')
        def _toggleGlobalMultiMode():
            print('GLOBAL MULTI TOGGLE')
        ## TODO: ADD GLOBAL LOOPING MODE
        self.audioDeviceLoopButton = FuncButton(SoundBackend.LoopTextState, _toggleGlobalLoopMod)
        self.audioDeviceLoopButton.setCheckable(True)
        
        ## TODO: ADD MULTI MODE
        self.audioDeviceMultiButton = FuncButton(SoundBackend.SpammingTextState, _toggleGlobalMultiMode)
        self.audioDeviceMultiButton.setCheckable(True)
        
        audioDeviceToggles.addWidget(self.audioDeviceLoopButton)
        audioDeviceToggles.addWidget(self.audioDeviceMultiButton)
        audioDeviceCanvas.addLayout(audioDevicePlaySpeedCanvas)
        audioDeviceCanvas.addLayout(audioDeviceToggles)
        # Audio Device Global Togglables END
        audioDeviceCanvas.addStretch(1)
        
    def _mediaControlsContent(self):
        pass
    def _soundboardTabsContent(self):
        # might not need a self var some of these
        self.soundboardTab = sections.SoundButtons('')
        self.slotsMonitorTab = sections.SlotStatusMonitor('')
        self.appSettingsTab = sections.PySoundboardSettings('')
        self.audioIndexMonitorTab = sections.AudioIndexMonitor('')
        
        self.soundboardTabsGroup.addTab(self.soundboardTab, 'Soundboard')
        self.soundboardTabsGroup.addTab(self.slotsMonitorTab, 'Slots')
        self.soundboardTabsGroup.addTab(self.appSettingsTab, 'Settings')
        self.soundboardTabsGroup.addTab(self.audioIndexMonitorTab, 'AudioIndex')
        
        

# Generic Button which allows for 
# Text and .clicked.connect() declaration
# on the same line
class FuncButton(QPushButton):
    def __init__(self, Name:str, callback, wh:tuple|None=None):
        super().__init__()
        if wh:
            width, height = wh
        else:
            width, height = 125, None
        # self.Method = Method
        self.setText(Name)
        self.setStyleSheet("text-align: left; padding: 5%; margin: 0%;")
        self.setFixedWidth(width) if width else ''
        self.setFixedHeight(height) if height else ''
        if not callable(callback):
            raise TypeError(f'{callback} Not Callable Method')
        self.clicked.connect(callback)

# Initialize Backend
AudioSystem = SoundBackend.InitializeAudioSystem()
AudioSystem.togglePoolRollOver('audio')
# buttonIndex = SoundBackend.GenerateSoundIndex(AudioSystem, SoundBackend.AudioFolder)
# Start Window
Main = MainWindow()
Main.show()
# SoundBackend.AudioSystem.status()
splash()
ShowSettings()
AudioSystem.addIndex(SoundBackend.SoundType.AUDIO_MEDIA,'./boop.wav')
AudioSystem.addIndex(SoundBackend.SoundType.AUDIO_MEDIA,'./startup.wav')

# try to look for a way to make this not be bound to only .wav files for startup sound!
# ^^^ In a way, this is already done.
# ^^^ Because  im using keyNames in Dicts now, which doesnt have file extensions.
# AudioSystem.toggleLooping('audio')
AudioSystem.loadAudioMedia('audio','startup',0)
AudioSystem.playSlot('audio',0)

sys.exit(APP.exec())