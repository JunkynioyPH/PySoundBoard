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
            soundButtonsCanvas = QVBoxLayout()
            self.buttonTabsCanvas = QTabWidget()
            self.setLayout(soundButtonsCanvas)
            soundButtonsCanvas.addWidget(self.buttonTabsCanvas)
            self.bakeButtons()
            
        def generateButtonIndex(self):
            return SoundBackend.GenerateSoundIndex(AudioSystem, SoundBackend.AudioFolder)
        def bakeButtons(self):
            self.buttonsIndex = self.generateButtonIndex()
            for _tabItem in self.buttonsIndex:
                tabCanvas = QWidget()
                tabContents = QHBoxLayout()
                buttonColumnCanvas = QVBoxLayout()
                buttonColumnCounter = 0
                # tabCanvas.setLayout(tabContents)
                for _buttonItem in self.buttonsIndex[_tabItem]:
                    if buttonColumnCounter < Settings['MaxRows']:
                        buttonColumnCanvas.addWidget(FuncButton(_buttonItem[0], _buttonItem[1], 120, styleSheet='text-align: left'))
                        buttonColumnCounter += 1
                    else:
                        # rich.print(f"[yellow b]Overflow[/yellow b] [red]{buttonColumnCounter, _tabItem, _buttonItem}")
                        buttonColumnCanvas.addStretch(0)
                        tabContents.addLayout(buttonColumnCanvas)
                        buttonColumnCanvas = QVBoxLayout()
                        buttonColumnCanvas.addWidget(FuncButton(_buttonItem[0], _buttonItem[1], 120, styleSheet='text-align: left'))
                        buttonColumnCounter = 1 ## 1 since i added a button from overflow of prev column
                else:
                    tabContents.addLayout(buttonColumnCanvas) if buttonColumnCounter != 0 else rich.print(f'[GUI] [green]Adding: Completed MaxRow[/green] [magenta b]<{_tabItem}>[/magenta b]')
                    tabContents.addStretch(0)
                    tabCanvas.setLayout(tabContents)
                    buttonColumnCanvas.addStretch(0) if buttonColumnCounter > 0 else ''
                    rich.print(f"[GUI] [yellow]Adding: Incomplete MaxRow[/yellow] [magenta b]<{_tabItem}>[/magenta b]") if buttonColumnCounter > 0 else rich.print('[GUI] [b]Perfect.[/b]')
                    self.buttonTabsCanvas.addTab(tabCanvas, _tabItem)
                    
        def refreshButtons(self):
            ...
            
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
class ArrowKeysFilter_Callback(QObject):
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

## Define Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.buttonSize = [120, 30]
        self.updaterLoop = updateTimerQueue(self, 125)
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
        topBarCanvas.addWidget(QLabel("PySoundboard PyQt6 - @junkynioy"))
        topBarCanvas.addWidget(self.topBarStatus)
        self.topBarStatus.setAlignment(AlignFlag.AlignHCenter)
        self.topBarStatus.setWordWrap(True)
        self.topBarStatus.setMinimumSize(600,38)
        self.topBarStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.audioDeviceControlsGroup = QGroupBox('')
        self.mediaControlsGroup = QGroupBox('')
        self.soundboardTabsGroup = QTabWidget()
        
        VerticalCanvas.addLayout(topBarCanvas)
        widgets = [self.audioDeviceControlsGroup, self.mediaControlsGroup, self.soundboardTabsGroup]
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
        audioDeviceSelectCanvas.addStretch(1)
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
        audioDeviceSelectCanvas.addStretch(1)
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
        self.audioDeviceVolumeSlider.setFixedSize(260,11)
        self.audioDeviceVolumeSlider.setRange(0, 100)
        audioDeviceVolumeControlCanvas.addWidget(self.audioDeviceVolumeSlider)
        self.audioDeviceVolumeSlider.setValue(int(Settings['Volume']))
        self.audioDeviceVolumeSlider.valueChanged.connect(_changeVolume)
        ### KeyFilter Event, Ai Assisted code START
        self.arrowKeys_saveVolume = ArrowKeysFilter_Callback(_saveVolume)
        self.audioDeviceVolumeSlider.installEventFilter(self.arrowKeys_saveVolume)
        ### Keyfilter Event, Ai Assisted code END
        self.audioDeviceVolumeSlider.sliderReleased.connect(_saveVolume)
        audioDeviceCanvas.addLayout(audioDeviceVolumeControlCanvas)
        # Audio Device Volume Control END
        # Audio Device Global PlaybackSpeed START
        audioDevicePlaySpeedCanvas = audioDeviceVolumeControlCanvas
        def _changeSpeed():
            self.audioDeviceSpeedLabel.setText(f"Playback Speed: {self.audioDeviceSpeedSlider.value()/100}x")
            for slot in range(0, AudioSystem.audioPoolSize):
                AudioSystem.setPlaybackSpeed('audio', slot, self.audioDeviceSpeedSlider.value()/100)
        def _speedSpeedToggle():
            self.audioDeviceSpeedSlider.setDisabled(False) if self.audioDeviceSpeedSyncToggle.isChecked() else self.audioDeviceSpeedSlider.setDisabled(True)
            rich.print("[PySoundboard] PlaybackSpeed Sync:", self.audioDeviceSpeedSyncToggle.isChecked())
            for slot in range(0, AudioSystem.audioPoolSize):
                AudioSystem.setPlaybackSpeed('audio', slot, 1) if not self.audioDeviceSpeedSyncToggle.isChecked() else AudioSystem.setPlaybackSpeed('audio', slot, self.audioDeviceSpeedSlider.value()/100)
        self.audioDeviceSpeedSlider = QSlider(Qt.Orientation.Horizontal)
        audioDeviceSpeedLabelCanvas = QHBoxLayout() # main canvas
        audioDeviceSpeedSyncToggleCanvas = QHBoxLayout() # canvas for speed display + sync toggle
        self.audioDeviceSpeedLabel = QLabel('Playback Speed: 1.00x')
        self.audioDeviceSpeedSyncToggle = QRadioButton()
        self.audioDeviceSpeedSyncToggle.setCheckable(True)
        self.audioDeviceSpeedSyncToggle.setChecked(True)
        self.audioDeviceSpeedSyncToggle.clicked.connect(_speedSpeedToggle)
        audioDeviceSpeedSyncToggleCanvas.addWidget(self.audioDeviceSpeedSyncToggle) # add toggle to speedsynccanvas
        audioDeviceSpeedSyncToggleCanvas.addWidget(QLabel('Sync')) # add toggle label for sync to speedsynccanvas
        audioDeviceSpeedLabelCanvas.addLayout(audioDeviceSpeedSyncToggleCanvas) # sync toggle + speed label to speedlabelcanvas
        audioDeviceSpeedLabelCanvas.addWidget(self.audioDeviceSpeedLabel) # add speed display to speedlabelcanvas
        audioDeviceSpeedLabelCanvas.addStretch(1)
        audioDevicePlaySpeedCanvas.addLayout(audioDeviceSpeedLabelCanvas) # add to main canvas
        audioDevicePlaySpeedCanvas.addWidget(self.audioDeviceSpeedSlider) # speed Slider
        self.audioDeviceSpeedSlider.setFixedHeight(11)
        self.audioDeviceSpeedSlider.setRange(5, 500)
        self.audioDeviceSpeedSlider.setValue(100)
        self.audioDeviceSpeedSlider.valueChanged.connect(_changeSpeed)
        # Audio Device Global PlaybackSpeed END
        # Audio Device Global Toggles START
        audioDeviceToggles = QVBoxLayout()
        def _toggleGlobalLoopMode():
            SoundBackend.ToggleLoopSync(AudioSystem) # Need to detatch AudioSystem sometime later
            self.audioDeviceLoopButton.setText(SoundBackend.LoopTextState)
            self.mediaLoopSlot.setDisabled(True) if self.audioDeviceLoopButton.isChecked() else self.mediaLoopSlot.setDisabled(False)
            self.mediaLoopSlot.setToolTip('Disabled as "Loop ALL" Enables loops to ALL slots.') if self.audioDeviceLoopButton.isChecked() else self.mediaLoopSlot.setToolTip('')
        def _toggleMultiMode():
            SoundBackend.ToggleSpamming()
            self.audioDeviceMultiButton.setText(SoundBackend.SpammingTextState)
        self.audioDeviceLoopButton = FuncButton(SoundBackend.LoopTextState, _toggleGlobalLoopMode, self.buttonSize[0], 30)
        self.audioDeviceLoopButton.setCheckable(True)
        self.audioDeviceMultiButton = FuncButton(SoundBackend.SpammingTextState, _toggleMultiMode, h=29)
        self.audioDeviceMultiButton.setCheckable(True)
        audioDeviceToggles.addWidget(self.audioDeviceLoopButton)
        audioDeviceToggles.addWidget(self.audioDeviceMultiButton)
        audioDeviceCanvas.addLayout(audioDeviceToggles)
        # Audio Device Global Toggles END
        audioDeviceCanvas.addStretch(1)
        
    def _mediaControlsContent(self):
        mediaControlsCanvas = QHBoxLayout()
        mediaControlsCanvas.addStretch(1)
        self.mediaControlsGroup.setLayout(mediaControlsCanvas)
        # Select Slot START
        self.mediaSlotSelector = QComboBox()
        def _changeSlot():
            SoundBackend.SelectedSlot = self.mediaSlotSelector.currentIndex()
        self.mediaSlotSelector.addItems([f"Slot {slot.name}" for slot in AudioSystem.audioPool['audio']])
        self.mediaSlotSelector.activated.connect(_changeSlot)
        self.mediaSlotSelector.setFixedHeight(30)
        mediaControlsCanvas.addWidget(self.mediaSlotSelector)
        # Select Slot END
        # Play Resume Stop Button START
        def _toggleAllPlayPauseState():
            SoundBackend.togglePlaybackStateAll(AudioSystem)
        def _stopAllPlayback():
            AudioSystem.unloadAllAudioMedia()
        self.mediaResumePauseButton = FuncButton('Resume / Pause', _toggleAllPlayPauseState, w=120, h=30)
        self.mediaStopButton = FuncButton('Stop', _stopAllPlayback, int(self.buttonSize[0]/2),self.buttonSize[1])
        mediaControlsCanvas.addWidget(self.mediaResumePauseButton)
        mediaControlsCanvas.addWidget(self.mediaStopButton)
        # Play Resume Stop Button END
        # Media position START
        def _updateMediaPositionSlider():
            _, dur, pos = AudioSystem.audioMediaPos('audio',SoundBackend.SelectedSlot)
            self.mediaCurrentPositionSlider.setRange(0, int(dur))
            self.mediaCurrentPositionSlider.setValue(int(pos)) if not self._pauseMediaPosUpdate else ''
        def _seekMedia():
            AudioSystem.audioPool['audio'][SoundBackend.SelectedSlot].setPosition(self.mediaCurrentPositionSlider.value()*1000)
            self._pauseMediaPosUpdate = False
        def _pauseMedia():
            self._pauseMediaPosUpdate = True
        def _updatePosDisplay(): 
            pos = self.mediaCurrentPositionSlider.value()
            self.mediaElapsedTimeLabel.setText(f"{pos} s" if pos < 60 else f"{round(pos/60,2)} min")
        self._pauseMediaPosUpdate = False
        self.mediaCurrentPositionSlider = QSlider(Qt.Orientation.Horizontal)
        self.mediaCurrentPositionSlider.setFixedWidth(245)
        self.updaterLoop.appendToQueue(_updateMediaPositionSlider)
        self.mediaCurrentPositionSlider.sliderPressed.connect(_pauseMedia)
        self.mediaCurrentPositionSlider.sliderMoved.connect(_updatePosDisplay)
        self.mediaCurrentPositionSlider.sliderReleased.connect(_seekMedia)
        mediaControlsCanvas.addWidget(self.mediaCurrentPositionSlider)
        # Media position END
        # Elapsed time START
        self.mediaElapsedTimeLabel = QLabel('---')
        self.mediaElapsedTimeLabel.setFixedWidth(100)
        def _updateElapsedTimeDisplay():
            self.mediaElapsedTimeLabel.setText(AudioSystem.audioMediaPos('audio', SoundBackend.SelectedSlot, True)) if not self._pauseMediaPosUpdate else ''
        self.updaterLoop.appendToQueue(_updateElapsedTimeDisplay)
        mediaControlsCanvas.addWidget(self.mediaElapsedTimeLabel)
        # Elapsed time END
        # Slot Loop START
        def _loopSlot():
            AudioSystem.toggleLoopAudioMediaSlot('audio', SoundBackend.SelectedSlot)
        self.mediaLoopSlot = FuncButton("Loop", _loopSlot, int(self.buttonSize[0]/2), self.buttonSize[1])
        mediaControlsCanvas.addWidget(self.mediaLoopSlot)
        # Slot Loop END
        mediaControlsCanvas.addStretch(1)
        
        
    def _soundboardTabsContent(self):
        # might not need a self var some of these
        self.soundboardTab = sections.SoundButtons('', self)
        self.slotsMonitorTab = sections.SlotStatusMonitor('', self)
        self.appSettingsTab = sections.PySoundboardSettings('', self)
        self.audioIndexMonitorTab = sections.AudioIndexMonitor('', self)
        
        self.soundboardTabsGroup.addTab(self.soundboardTab, 'Soundboard')
        self.soundboardTabsGroup.addTab(self.slotsMonitorTab, 'Slots')
        self.soundboardTabsGroup.addTab(self.appSettingsTab, 'Settings')
        self.soundboardTabsGroup.addTab(self.audioIndexMonitorTab, 'AudioIndex')
    ## Ai Assisted Window centering
    ## Unknown if Cross Platform
    def center_window(self):
        screen = self.screen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())
        
# Generic Button which allows for 
# Text and .clicked.connect() declaration
# on the same line
class FuncButton(QPushButton):
    def __init__(self, Name:str, callback, w:int|None=None, h:int|None=None, styleSheet:str|None=None):
        super().__init__()
        # self.Method = Method
        self.setText(Name)
        self.setStyleSheet(f"padding: 5%;{f' {styleSheet}' if styleSheet else ''}") #  margin: 0%; ; 
        self.setFixedWidth(w) if w else ''
        self.setFixedHeight(h) if h else ''
        # if not callable(callback):
        #     raise TypeError(f'{callback} Not Callable Method')
        self.clicked.connect(callback)

# Initialize Backend
AudioSystem = SoundBackend.InitializeAudioSystem()
AudioSystem.togglePoolRollOver('audio')
# buttonIndex = SoundBackend.GenerateSoundIndex(AudioSystem, SoundBackend.AudioFolder)
# Start Window
Main = MainWindow()
Main.show()
Main.center_window()
# SoundBackend.AudioSystem.status()
splash()
ShowSettings()
# AudioSystem.addIndex(SoundBackend.SoundType.AUDIO_MEDIA,'./boop.wav')
AudioSystem.addIndex(SoundBackend.SoundType.AUDIO_MEDIA,'./startup.wav')

# try to look for a way to make this not be bound to only .wav files for startup sound!
# ^^^ In a way, this is already done.
# ^^^ Because  im using keyNames in Dicts now, which doesnt have file extensions.
# AudioSystem.toggleLooping('audio')
AudioSystem.loadAudioMedia('audio','startup',0)
AudioSystem.playSlot('audio',0)

sys.exit(APP.exec())