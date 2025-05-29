from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QRegion
# Looks like PyQt6 has some sound capabilities, might re-write Soundboard_Backend to be fully PyQt
from PyQt6.QtMultimedia import QAudioSource, QAudioFormat, QAudioBufferInput, QAudioBufferOutput # Maybe i can get an audio visualiser out of this..?
from PyQt6.QtWidgets import *

from pygame import mixer
import time, json, os
import Soundboard_Backend_PyG as SoundBackend


# Console splash
def splash():
    os.system('cls' if os.name=='nt' else 'clear')
    os.system('title PySoundBoard Backend') if os.name=='nt' else print('PySoundBoard Backend')
    print('''

    ██████╗ ██╗   ██╗███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██████╗  ██████╗  █████╗ ██████╗ ██████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
    ██████╔╝ ╚████╔╝ ███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║ Q
    ██╔═══╝   ╚██╔╝  ╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║ T
    ██║        ██║   ███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
                        Written By : @Junkynioy - https://github.com/JunkynioyPH
    ''')
splash()

# Prelims
DefaultValSettings = ["CABLE Input (VB-Audio Virtual Cable)","VoiceMeeter Input (VB-Audio VoiceMeeter VAIO)",None]
# Load Settings
InitializeSettings, Settings = SoundBackend.InitializeSettings, SoundBackend.Settings

def ShowSettings():
    print("\n[Current Settings]")
    for i in Settings:
        print(f"[{i}] ---> [{Settings[i]}]")

def UpdateSettings(Variable,Value):
    print(f"\n------------\nUpdating {Variable} to {Value}")
    Settings[Variable] = Value
    with open("Settings.json","w") as UpdateSettings:
        UpdateSettings.write(json.dumps(Settings))
    InitializeSettings() # Reload Settings
    ShowSettings()
    print("\nSettings Updated!\n------------")

tries, index = 0, 0
limit = int(len(DefaultValSettings)+1) # unused yet
def InitializeAudioSystem():
    global tries, index
    # if tries < limit:
    #     try:
            # perhaps make the frequency + buffer configurable in the future.
            # frequency=48000
    if Settings['AudioDevice'] is None:
        print('\nVB-Audio VoiceMeeter/VB-Audio Virtual Cable [NOT FOUND]\nUsing [System Default Output] !\n\nIf you do have an Output Device you wish to use, specify\nit in the [AudioDevice Input-Box] or in [Settings.json]\nIf you now have VoiceMeeter or VB-Cable Installed, Press "Set Device" Button to Apply.')
    mixer.pre_init(devicename=Settings["AudioDevice"])
    mixer.init()
    mixer.music.set_volume(float(Settings['Volume'])/100)
            # try:
    SoundBackend.SoundButton(r"..\startup.wav").Play() #try to look for a way to make this not be bound to only .wav files for startup sound!
    #         except Exception as ERR:
    #             PrintErr(f"InitializeAudioSystem()",ERR)
    #     except Exception as Err:
    #         time.sleep(1)
    #         tries += 1
    #         print(Settings)
    #         PrintErr("InitializeAudioSystem()",f"{Settings['AudioDevice']} - {Err}")
    #         print("Attempting Fixes...")
            
    #         if str(Err).lower() == 'no such device.' and index < len(DefaultValSettings):
    #             print(f"{index, str(Err).lower()} Setting AudioDevice to [{DefaultValSettings[index]}]")
    #             UpdateSettings("AudioDevice",DefaultValSettings[index])
    #             index += 1

    #         AudioDevice.set(Settings["AudioDevice"])
    #         InitializeAudioSystem()
    #         # clearconsole()
    # else:
    #     PrintErr("InitializeAudioSystem()","\nMaximum retries Reached.\nPlease Check Settings.json\nThis can only be triggered in a manual way, so consult the 'Issues' tab on github if needed.")
    #     time.sleep(10)
    #     exit()
InitializeSettings()
ShowSettings()
InitializeAudioSystem()


# Show First-Time Execution then turn off pop up
# need to replace
if int(Settings["Splash"]) == "1":
    os.system('python Splash.py')
    UpdateSettings("Splash","0")

## Define Main Window
AlignFlag = Qt.AlignmentFlag

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Partially weird that i have to add self as parent to this QTimer
        windowTitleNP = QTimer(self)
        windowTitleNP.timeout.connect(self.WindowTitleNowPlaying)
        windowTitleNP.start(100)
        # self.setFixedSize(self.size())

        ## Define Containers
        # Modifiable Space
        Canvas = QWidget() 
        self.setCentralWidget(Canvas)
        # Main Modifiable Space
        VCanvas = QVBoxLayout()
        Canvas.setLayout(VCanvas)
        # Create Groups and contents
        AudioDeviceDisplay = QGroupBox("   Audio Device ")
        VCanvas.addWidget(AudioDeviceDisplay)
        AudioDeviceDisplay.setLayout(self.AudioDeviceDisplayContent())
        
        Controls = QGroupBox("   Controls ")
        VCanvas.addWidget(Controls)
        Controls.setLayout(self.ControlsContent())
        
        SoundButtons = QGroupBox("   Sounds ")
        VCanvas.addWidget(SoundButtons)
        SoundButtons.setLayout(self.SoundButtonsContent())

    # Dynamic Window Title for Now Playing sound
    def WindowTitleNowPlaying(self):
        MainFrame.setWindowTitle(f"PySoundboard PyQt6 - Junkynioy - File: {SoundBackend.Title}")
        
    # Define Contents of Each Groups
    ## Audio Set Device Section
    def AudioDeviceDisplayContent(self):
        layout = QHBoxLayout()
        return layout
    
    ## Controls Section
    def ControlsContent(self):
        layout = QHBoxLayout()
        ControlButton = FuncButton
        # layout.addStretch(1)
        layout.addWidget(ControlButton('Pause',self.Pause))
        layout.addWidget(ControlButton('Resume',self.Resume))
        layout.addWidget(ControlButton('Stop',self.Stop))
        layout.addWidget(self.SoundTimeElapsed())
        layout.addLayout(self.VolumeSlider())
        layout.addLayout(self.Toggles())
        layout.addStretch(1)
        
        return layout
    class VolumeSlider(QHBoxLayout):
        def __init__(self):
            super().__init__()
            self.label = QLabel(f"{Settings['Volume']} %")
            self.slider = QSlider(Qt.Orientation.Horizontal)
            self.slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
            self.slider.setRange(0,100)
            self.addWidget(self.label)
            self.label.setFixedWidth(35)
            self.addWidget(self.slider)
            self.slider.setValue(int(Settings['Volume']))
            self.slider.valueChanged.connect(self.changeVolume) # live sound volume change
            self.slider.sliderReleased.connect(self.saveVolume) # save on release  
        def changeVolume(self):
            Volume = self.slider.value()
            self.label.setText(f"{int(Volume)} %")
            mixer.music.set_volume(Volume/100)
        def saveVolume(self):
            UpdateSettings("Volume", self.slider.value())
    class SoundTimeElapsed(QLabel):
        def __init__(self):
            super().__init__()
            self.setFixedWidth(120)
            self.Timer = QTimer()
            self.Timer.timeout.connect(self.labelText)
            self.Timer.start(100)
        def labelText(self):
            self.setText(f"Elapsed: {mixer.music.get_pos()/1000} s") if int(mixer.music.get_pos()/1000) < 60 else self.setText(f"Elapsed: {round(mixer.music.get_pos()/60000,2)} min")
    class Toggles(QHBoxLayout):
        def __init__(self):
            super().__init__()
            # Looping
            self.loopToggle = FuncButton(f'{SoundBackend.LoopTextState}',self.Loop)
            self.loopToggle.setCheckable(True) # Mainly Visual, we already have the text changing
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
    def Resume(self):
        if mixer.music.get_pos() > 0:
            mixer.unpause()
            mixer.music.unpause()
    def Pause(self):
        mixer.pause()
        mixer.music.pause() 
    def Stop(self):
        self.Resume()
        mixer.fadeout(250)
        mixer.music.fadeout(250)
    
    ## Sound Buttons Section
    def SoundButtonsContent(self):
        # soon add tabs for each folder, so we'll need to rewrite SoundBtnDef.py to add an index of folders which contains sound files
        SoundButton = FuncButton
        layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()
        index = 0
        indexRange: int = int(Settings["MaxRows"])
        indexCounter = 0
        for each in SoundBackend.ComDispName:
            layoutV.addWidget(SoundButton(each[0],each[1]))
            index += 1
            indexCounter += 1
            # New Column every MaxRow
            if indexCounter == indexRange:
                layoutV.addStretch(0)
                layoutH.addLayout(layoutV)
                layoutV = QVBoxLayout()
                indexCounter = 0
        else:
            layoutH.addLayout(layoutV) if indexCounter != 0 else print('\nAdded: Completed MaxRow')
            layoutV.addStretch(0) if indexCounter > 0 else ''
            print("\nAdding: Incomplete MaxRow") if indexCounter > 0 else print('Perfect.')
        layoutH.addStretch(0)
        return layoutH

# Generic Button which allows for 
# Text and .clicked.connect(classmethod) declaration
# on the same line
class FuncButton(QPushButton):
    def __init__(self, Name:str, Method:classmethod):
        super().__init__()
        self.setText(Name)
        self.setStyleSheet("text-align: left; padding: 5%; margin: 0%;")
        self.setFixedWidth(125)
        self.clicked.connect(Method)

# Start Window
APP = QApplication([])
MainFrame = MainWindow()
MainFrame.show()
APP.exec()