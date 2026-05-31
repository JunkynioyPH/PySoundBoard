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

# Pretty Print Override
# immutable?
rprint = rich.print


# Console splash
def splash():
    # os.system('cls' if os.name=='nt' else 'clear')
    os.system('title PySoundBoard Backend') if os.name=='nt' else rprint('\nPySoundBoard Backend')
    rprint('''

    ██████╗ ██╗   ██╗███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██████╗  ██████╗  █████╗ ██████╗ ██████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
    ██████╔╝ ╚████╔╝ ███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║ Q
    ██╔═══╝   ╚██╔╝  ╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║ T
    ██║        ██║   ███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
                        Written By : @Junkynioy - https://github.com/JunkynioyPH
    ''')


# Patch to make old code functional
SoundBackend.InitializeSettings()
AudioSystem = SoundBackend.InitializeAudioSystem()
AudioSystem.togglePoolRollOver('audio')
buttonIndex = SoundBackend.GenerateSoundIndex(AudioSystem, SoundBackend.AudioFolder)

# Load Settings
Settings = SoundBackend.Settings

if not Settings['UseSystemTheme']:
    APP.setStyle('Fusion')
    APP.setPalette(darkmode.get_slate_blue_dark_palette())
    rprint('[PySoundboard] Using Built-in Dark Theme')
    
else:
    rprint('[PySoundboard] Using System Theme')
    
def ShowSettings():
    rprint("[PySoundboard] ", end='')
    for i in Settings:
        rprint(f"[yellow][{i}:{Settings[i]}][/yellow] ", end='')
    else:
        rprint()

def UpdateSettings(Variable,Value):
    rprint(f"[PySoundboard] [green]Update Setting:[/green] <{Variable}> to '{Value}'")
    Settings[Variable] = Value
    with open("Settings.json","w") as UpdateSettings:
        UpdateSettings.write(json.dumps(Settings))
    SoundBackend.InitializeSettings() # Reload Settings
    ShowSettings()

# Show First-Time Execution then turn off pop up
# need to replace
if Settings["Splash"] == True:
    # os.system('python Splash.py')
    rprint('='*20)
    UpdateSettings("Splash",False)

## Define Main Window
AlignFlag = Qt.AlignmentFlag
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Partially weird that i have to add self as parent to this QTimer
        self.updateTimerLoop = self.GlobalTimerQueue(self)
        self.updateTimerLoop.updateList.append(self.WindowTitleNowPlaying)
        # self.setFixedSize(self.size())

        ## Define Containers
        # Modifiable Space
        Canvas = QWidget() 
        self.setCentralWidget(Canvas)
        # Main Modifiable Space
        VCanvas = QVBoxLayout()
        Canvas.setLayout(VCanvas)
        
        
        # Create Groups and contents
        AudioDeviceDisplay = QGroupBox("   AudioDevice Controls ")
        VCanvas.addWidget(AudioDeviceDisplay)
        AudioDeviceDisplay.setLayout(self.AudioDeviceContent())
        
        Controls = QGroupBox("   Media Controls ")
        VCanvas.addWidget(Controls)
        Controls.setLayout(self.ControlsContent())
        
        SoundButtons = QTabWidget()
        VCanvas.addWidget(SoundButtons)
        InterfaceCanvas = QWidget()
        slotsMonitoringCanvas = QWidget() 
        slotsMonitoringContainer = QVBoxLayout() 
        slotsMonitoringCanvas.setLayout(slotsMonitoringContainer)
        slotsMonitoringContainer.addLayout(self.monitoringContents())
        
        InterfaceCanvas.setLayout(self.SoundButtonsContent())
        SoundButtons.addTab(InterfaceCanvas, "  Soundboard ")
        SoundButtons.addTab(slotsMonitoringCanvas, ' Slots Monitoring ')

    #     # Debug
    #     audioSystemStatus = QTimer(self)
    #     audioSystemStatus.timeout.connect(self.statusDebug)
    #     audioSystemStatus.start(500)
    #     # Debug 
    #     self.AudioSystemStatusDisplay = QLabel()
    #     self.AudioSystemStatusDisplay.setFixedWidth(950)
    #     self.AudioSystemStatusDisplay.setWordWrap(True)
    #     VCanvas.addWidget(self.AudioSystemStatusDisplay)
    # # Debug
    # def statusDebug(self):
    #     self.AudioSystemStatusDisplay.setText(f"{AudioSystem.status(cli=False)}\n{AudioSystem.hostAudioPoolStatus() if os.name=='posix' else ''}")
    #     # AudioSystem.linkAudioMediaToHost()
        
    class GlobalTimerQueue(QTimer):
        def __init__(self, parent):
            super().__init__(parent)
            self.updateList:list = []
            self.timeout.connect(self.update)
            self.start(125)
            
        def update(self):
            for item in self.updateList:
                item()

    # Dynamic Window Title for Now Playing sound
    def WindowTitleNowPlaying(self):
        MainFrame.setWindowTitle(f"PySoundboard PyQt6 - Junkynioy - File: {SoundBackend.Title}")
        # print(self.audioPoolText)
    
    # Define Contents of Each Groups
    ## Audio Monitoring Section
    def monitoringContents(self):
        layout = QVBoxLayout()
        class SlotMonitoring(QGroupBox):
            def __init__(self, slot):
                super().__init__()
                self.slot = slot
                self.canvas = QVBoxLayout()
                self.controls = QHBoxLayout()
                self.setLayout(self.canvas)
                self.canvas.addLayout(self.controls)
                self.Updater()
                self.system = AudioSystem
                self.slotObject = self.system.audioPool.get('audio')[self.slot]
                
                addW = self.controls.addWidget
                width = 65
                
                addW(FuncButton("Resume", lambda: self.system.playSlot('audio',self.slot), width))
                addW(FuncButton("Pause", lambda: self.system.pauseSlot('audio',self.slot), width))
                addW(FuncButton("Stop", lambda: self.system.stopSlot('audio',self.slot), width))
                addW(FuncButton("Unload", lambda: self.system.unloadAudioMediaSlot('audio',self.slot), width))
                # self.toggleLoopButton = FuncButton("Looping", lambda: '', width)
                # self.toggleLoopButton.setCheckable(True)
                # addW(self.toggleLoopButton)
                # self.controls.addLayout(self.toggles())
                self.controls.addStretch()
                
                # self.canvas.addLayout()
                
            def Updater(self):
                timer = QTimer(self)
                def title():
                    self.setTitle(f"Slot #{self.slot} :-: {repr(self.slotObject)}")
                    # self.slotObject.setLoops(int(((2**32) / 2) - 1)) if self.toggleLoopButton.isChecked() else self.slotObject.setLoops(1)
                    
                timer.timeout.connect(title)
                timer.start(250)
            
            # def toggleLoop(self):
            #     self.slotObject.setLoops(int(((2**32) / 2) - 1) if self.slotObject.loops() < 2 else 1)
            
            def toggles(self):
                toggles = QHBoxLayout()
                toggles.addWidget(QLabel('Sync:'))
                SyncVolume, SyncSpeed, SyncLoop = QCheckBox(), QCheckBox(), QCheckBox()
                SyncVolume.setChecked(True)
                SyncSpeed.setChecked(True)
                SyncLoop.setChecked(True)
                
                toggles.addWidget(SyncVolume)
                toggles.addWidget(QLabel('Volume'))
                toggles.addWidget(SyncLoop)
                toggles.addWidget(QLabel('Loop'))
                toggles.addWidget(SyncSpeed)
                toggles.addWidget(QLabel('Speed'))
                
                toggles.addStretch()
                
                return toggles
                
        for slotItem in range(0,AudioSystem.audioPoolSize):
            slotMonitoringObject:SlotMonitoring = SlotMonitoring(slotItem)
            layout.addWidget(slotMonitoringObject)
        else:
            layout.addStretch()
                
        return layout
    ## Audio Set Device Section
    class AudioDeviceContent(QHBoxLayout):
        def __init__(self):
            super().__init__()
            # self.addStretch()
            self.addWidget(QLabel("Device:"))
            self.deviceList:list = [device.description() for device in QMediaDevices.audioOutputs()]
            self.comboList = QComboBox()
            self.comboList.setFixedWidth(370)
            self.comboList.setFixedHeight(20)
            self.comboList.setPlaceholderText("Select an output device...")
            self.comboList.addItems(self.deviceList)
            # self.indexDevices()
            # self.comboList.setCurrentText(Settings["AudioDevice"])
            self.comboList.setCurrentIndex(self.comboList.findText(Settings["AudioDevice"]))
            self.comboList.activated.connect(self.changeDevice)
            # self.addWidget(FuncButton("Set Device", self.changeDevice))
            self.addWidget(self.comboList)
            self.addLayout(self.VolumeSlider())
            self.addStretch()
            
        def changeDevice(self):
            def _getDevice():
                devices = QMediaDevices.audioOutputs()
                for device in devices:
                    if device.description() == self.comboList.currentText():
                        print(device, device.description(), self.comboList.currentText())
                        return device
            try:
                UpdateSettings("AudioDevice",self.comboList.currentText())
                AudioSystem.setDevice(_getDevice(), True)
                # SoundBackend.SoundFile('./startup.wav').Play()
                AudioSystem.loadAudioMedia('audio','startup',0) ###########
                AudioSystem.playAll()######################
                splash()
                rprint(f"[PySoundboard] <{f'Default Device"{Settings["AudioDevice"]}"' if Settings["AudioDevice"] is None else self.comboList.currentText()}> Found!\n[PySoundboard] Successfully Bound to Device!")
            except Exception as Err:
                splash()
                rprint('[PySoundboard] System Defaulting!')
                UpdateSettings("AudioDevice", None)
                AudioSystem.setDevice(QMediaDevices.defaultAudioOutput(), True)
                AudioSystem.loadAudioMedia('audio','startup',0) ###########
                AudioSystem.playAll()######################
                rprint(f"[PySoundboard] [{self.comboList.currentText()}] : {Err}\n[PySoundboard] Restart Soundboard to refresh Dropdown List ") if self.comboList.currentIndex() != 0 else ''
        class VolumeSlider(QHBoxLayout):
            def __init__(self):
                super().__init__()
                self.label = QLabel(f"Volume: {Settings['Volume']} %")
                self.slider = QSlider(Qt.Orientation.Horizontal)
                self.slider.setFixedWidth(100)
                self.slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
                self.slider.setRange(0,100)
                self.addWidget(self.label)
                self.label.setFixedWidth(80)
                self.addWidget(self.slider)
                self.slider.setValue(int(Settings['Volume']))
                self.slider.valueChanged.connect(self.changeVolume) # live sound volume change
                self.slider.sliderReleased.connect(self.saveVolume) # save on release  
            def changeVolume(self):
                Volume = self.slider.value()
                self.label.setText(f"Volume: {int(Volume)} %")
                AudioSystem.setVolume('audio', Volume)
            def saveVolume(self):
                UpdateSettings("Volume", self.slider.value())
                # Janky asf but it gets the job done.
                # AudioSystem.play('audio','boop') if AudioSystem.audioPool['audio'][0].playbackState() in (AudioSystem.audioPool['audio'][0].PlaybackState.StoppedState, AudioSystem.audioPool['audio'][0].PlaybackState.PausedState) else ''
    
    ## Controls Section
    def ControlsContent(self):
        ControlButton = FuncButton
        layout = QHBoxLayout()
        # layout.addStretch(1)
        layout.addWidget(self.SlotSelector(self))
        layout.addWidget(ControlButton('Resume / Pause',self.togglePlaybackState))
        layout.addWidget(ControlButton('Stop',self.Stop))
        layout.addWidget(self.SoundTimeElapsed(self))
        layout.addLayout(self.Toggles())
        layout.addStretch(1)
        
        return layout
    
    class SlotSelector(QComboBox):
        def __init__(self, parent:"MainWindow"):
            super().__init__()
            self.addItems([f"Slot {slot.name}" for slot in AudioSystem.audioPool['audio']])
            self.activated.connect(self.changeSlot)
            parent.updateTimerLoop.updateList.append(self.toggleSelectorDisabled)
            
        def changeSlot(self):
            SoundBackend.SelectedSlot = self.currentIndex()
            print(SoundBackend.SelectedSlot)
        def toggleSelectorDisabled(self):
            if SoundBackend.SpammingState == 1:
                self.setDisabled(True)
                self.setToolTip('This is Locked when MultiMode is Enabled. Multimode automatically manages Available Slots.')
            else:
                self.setDisabled(False)
                self.setToolTip('')
            
    class SoundTimeElapsed(QLabel):
        def __init__(self, parent:"MainWindow"):
            super().__init__()
            self.setFixedWidth(125)
            parent.updateTimerLoop.updateList.append(self.labelText)
        def labelText(self):
            self.setText(AudioSystem.audioMediaPos('audio',SoundBackend.SelectedSlot,True))
    class Toggles(QHBoxLayout):
        def __init__(self):
            super().__init__()
            # Looping
            self.loopToggle = FuncButton(f'{SoundBackend.LoopTextState}',self.Loop)
            self.loopToggle.setCheckable(True) # Mainly Visual, we already have the text changing
            # self.slotSelectoritem = slotselector
            self.addWidget(self.loopToggle)
            
            # Multi-Mode
            self.multiToggle = FuncButton(f'{SoundBackend.SpammingTextState}',self.Multi)
            self.multiToggle.setCheckable(True)
            self.addWidget(self.multiToggle)
        def Loop(self):
            SoundBackend.ToggleLoop()
            self.loopToggle.setText(f"{SoundBackend.LoopTextState}")
        def Multi(self):
            SoundBackend.ToggleSpamming()
            self.multiToggle.setText(f"{SoundBackend.SpammingTextState}")
            
            
    # Typical controls
    def togglePlaybackState(self):
        SoundBackend.TogglePlaybackStateAll(AudioSystem)
        # AudioSystem.playAll()
    def Stop(self):
        # AudioSystem.stopAll()
        AudioSystem.unloadAllAudioMedia()
        # mixer.fadeout(250)
        # mixer.music.fadeout(250)
    
    ## Sound Buttons Section
    def SoundButtonsContent(self):
        SoundButton = FuncButton
        layout = QHBoxLayout()
        tabs =  QTabWidget()
        
        # create tablist
        layout.addWidget(tabs)
        indexRange: int = int(Settings["MaxRows"])
        # add them buttons to their own tab
        for tabName in buttonIndex:
            content = QWidget() # create a widget which holds all sound buttons for that tab
            layoutH = QHBoxLayout() # button layout
            layoutV = QVBoxLayout() # button layout
            index = 0
            # each entry in SoundBackend.ComDispName
            for soundButton in buttonIndex[tabName]:
                layoutV.addWidget(SoundButton(soundButton[0],soundButton[1]))
                index += 1
                # if it reaches max range, add new column
                if index == indexRange:
                    layoutV.addStretch(0)
                    layoutH.addLayout(layoutV)
                    layoutV = QVBoxLayout()
                    index = 0
            else:
                # force add remaining layoutH and add Stretch, then add tab with the contents
                layoutH.addLayout(layoutV) if index != 0 else rprint(f'[GUI] [green]Adding: Completed MaxRow[/green] [magenta b]<{tabName}>[/magenta b]')
                layoutH.addStretch(0)
                content.setLayout(layoutH)
                layoutV.addStretch(0) if index > 0 else ''
                rprint(f"[GUI] [yellow]Adding: Incomplete MaxRow[/yellow] [magenta b]<{tabName}>[/magenta b]") if index > 0 else rprint('[GUI] [b]Perfect.[/b]')
                tabs.addTab(content,tabName)
        return layout

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
ShowSettings()
# Start Window
MainFrame = MainWindow()
MainFrame.show()
# AudioSystem.status()
AudioSystem.addIndex(SoundBackend.SoundType.AUDIO_MEDIA,'./boop.wav')
AudioSystem.addIndex(SoundBackend.SoundType.AUDIO_MEDIA,'./startup.wav')

# try to look for a way to make this not be bound to only .wav files for startup sound!
# ^^^ In a way, this is already done.
# ^^^ Because  im using keyNames in Dicts now, which doesnt have file extensions.
AudioSystem.loadAudioMedia('audio','startup',0)
AudioSystem.playSlot('audio',0)

sys.exit(APP.exec())