from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QRegion
from PyQt6.QtWidgets import *
from pygame import mixer
import time, json, os
import SoundBtnDef as SD


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
InitializeSettings, Settings = SD.InitializeSettings, SD.Settings

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
    SD.SoundButton(r"..\startup.wav").Play() #try to look for a way to make this not be bound to only .wav files for startup sound!
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
        self.setWindowTitle("PySoundboard PyQt6 - Junkynioy") # temporary cuz it will be dynamic based on what sound is playing
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

    # Define Contents of Each Groups
    ## Audio Set Device Section
    def AudioDeviceDisplayContent(self):
        layout = QHBoxLayout()
        return layout
    
    ## Controls Section
    def ControlsContent(self):
        layout = QHBoxLayout()
        ControlButton = FuncButton
        layout.addWidget(self.SoundLoadedTitle()) # for now this is how ill change title to have loaded filename
        layout.addWidget(ControlButton('Pause',self.Pause))
        layout.addWidget(ControlButton('Resume',self.Resume))
        layout.addWidget(ControlButton('Stop',self.Stop))
        layout.addWidget(self.SoundTimeElapsed())
        layout.addLayout(self.VolumeSlider())
        layout.addStretch(1)
        
        return layout
    class VolumeSlider(QHBoxLayout):
        def __init__(self):
            super().__init__()
            self.label = QLabel(f"{Settings['Volume']} %")
            self.slider = QSlider(Qt.Orientation.Horizontal)
            self.slider.setRange(0,100)
            self.addWidget(self.label)
            self.label.setFixedWidth(35)
            self.addWidget(self.slider)
            self.slider.setValue(int(Settings['Volume']))
            self.slider.valueChanged.connect(self.changeVolume)
            
        def changeVolume(self):
            Volume = self.slider.value()
            self.label.setText(f"{int(Volume)} %")
            mixer.music.set_volume(Volume/100)
            splash()
            UpdateSettings("Volume",Volume) # find a way to not write immediately after ' .valueChanged' cuz im sure that scratches the HDD/SSD on the "write" department

    # Change title depending on what song is loaded (maybe there is a better way of doing this without a QLabel...)
    class SoundLoadedTitle(QLabel):
        def __init__(self):
            super().__init__()
            self.setFixedSize(0,0)
            self.Timer = QTimer()
            self.Timer.timeout.connect(self.labelText)
            self.Timer.start(100)
        def labelText(self):
            MainFrame.setWindowTitle(f"PySoundboard PyQt6 - Junkynioy - File: {SD.Title}")
            
    # Label specifically for displaying elapsed time since audio started playing
    class SoundTimeElapsed(QLabel):
        def __init__(self):
            super().__init__()
            self.setFixedWidth(120)
            self.Timer = QTimer()
            self.Timer.timeout.connect(self.labelText)
            self.Timer.start(100)
        def labelText(self):
            self.setText(f"Elapsed: {mixer.music.get_pos()/1000} s") if int(mixer.music.get_pos()/1000) < 60 else self.setText(f"Elapsed: {round(mixer.music.get_pos()/60000,2)} min")
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
        for each in SD.ComDispName:
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