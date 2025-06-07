from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QRegion # MAYBE ill get to work this at some point lmao
from PyQt6.QtMultimedia import QMediaDevices # for specifically setting the audio Device. Backend will read Settings.json
from PyQt6.QtWidgets import *
# from pygame import mixer # Commented to see clearly my reliance on pygame.mixer on the front-end
import json, os, sys
import Soundboard_Backend_PyQt6 as SoundBackend

# Console splash
def splash():
    os.system('cls' if os.name=='nt' else 'clear')
    _ = QMediaDevices.audioOutputs() # Moving the FFMPEG thing
    del _
    os.system('title PySoundBoard Backend') if os.name=='nt' else print('\nPySoundBoard Backend')
    print('''

    ██████╗ ██╗   ██╗███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██████╗  ██████╗  █████╗ ██████╗ ██████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
    ██████╔╝ ╚████╔╝ ███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║ Q
    ██╔═══╝   ╚██╔╝  ╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║ T
    ██║        ██║   ███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
                        Written By : @Junkynioy - https://github.com/JunkynioyPH
    ''')


# Prelims
DefaultValSettings = ["CABLE Input (VB-Audio Virtual Cable)","VoiceMeeter Input (VB-Audio VoiceMeeter VAIO)",None]
InitializeAudioSystem = SoundBackend.InitializeAudioSystem
# Load Settings
Settings = SoundBackend.Settings
def ShowSettings():
    print("\n[Current Settings]")
    for i in Settings:
        print(f"[{i}] ---> [{Settings[i]}]")

def UpdateSettings(Variable,Value):
    print(f"\n------------\nUpdating [{Variable}] to [{Value}]")
    Settings[Variable] = Value
    with open("Settings.json","w") as UpdateSettings:
        UpdateSettings.write(json.dumps(Settings))
    SoundBackend.InitializeSettings() # Reload Settings
    ShowSettings()
    print("\n------------\n")

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
        AudioDeviceDisplay.setLayout(self.AudioDeviceContent())
        
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
    class AudioDeviceContent(QHBoxLayout):
        def __init__(self):
            super().__init__()
            self.deviceList:list = []
            self.deviceInfo = []
            self.comboList = QComboBox()
            self.comboList.setFixedWidth(370)
            self.indexDevices()
            self.comboList.setCurrentText(Settings["AudioDevice"])
            self.comboList.activated.connect(self.indexDevices)
            self.addWidget(FuncButton("Set Device", self.changeDevice))
            self.addWidget(self.comboList)
            self.addStretch(0)
        def indexDevices(self):
            # When new devices are added, this adds them automatically
            # but when devices are removed, it still appears on the list
            self.deviceInfo = QMediaDevices.audioOutputs() 
            # ##### #
            
            comboCount, deviceCount = self.comboList.count()-1, len(self.deviceInfo)
            self.deviceList.clear() if deviceCount != comboCount else '' #print('No Device Count Change. deviceList not cleared')
            self.comboList.clear() if deviceCount != comboCount else '' #print('No Device Count Change. comboList not cleared')
            if deviceCount != comboCount:
                for each in self.deviceInfo:
                    self.deviceList.append(each.description())
                else:
                    self.comboList.addItem('Select a Device... or Reload List (Default Output Device)')
                    self.comboList.addItems(self.deviceList)
                    # print('Audio List Compiled.')
                    # print(f"{len(self.deviceInfo)} - {self.comboList.count()-1}")
            # else: 
            #     print('No Device Count Changes were made. ')
            # print(f"{len(self.deviceInfo)} - {self.comboList.count()-1}")
        def changeDevice(self):
            try:
                UpdateSettings("AudioDevice",self.comboList.currentText())
                mixer.quit()
                InitializeAudioSystem()
                splash()
                print(f"\n{'*'*10}\n[{f'Default Device "{Settings["AudioDevice"]}"' if Settings["AudioDevice"] is None else self.comboList.currentText()}] Found!\nSuccessfully Bound to Device!\n{'*'*10}")
            except Exception as Err:
                # PrintErr("ChangeAudioDevice()",Err)
                print('???? System Defaulting!')
                UpdateSettings("AudioDevice", None)
                InitializeAudioSystem()
                print(f"\n???? [{self.comboList.currentText()}] : {Err}\n???? Restart Soundboard to refresh Dropdown List ") if self.comboList.currentIndex() != 0 else ''
                # AudioDevice.set(Settings["AudioDevice"])
            
    ## Controls Section
    def ControlsContent(self):
        layout = QHBoxLayout()
        ControlButton = FuncButton
        # layout.addStretch(1)
        layout.addWidget(ControlButton('Resume',self.Resume))
        layout.addWidget(ControlButton('Pause',self.Pause))
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
        # Disabled for now to make the GUI work
        def labelText(self):
            pass
            # self.setText(f"Elapsed: {mixer.music.get_pos()/1000} s") if int(mixer.music.get_pos()/1000) < 60 else self.setText(f"Elapsed: {round(mixer.music.get_pos()/60000,2)} min")
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
            layoutV.addWidget(SoundButton(each[1],each[2])) # 0 = TabName / 1 = Sound Name / 2 = classmethod
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

# Initialize Backend
splash()
ShowSettings()
InitializeAudioSystem()

# Start Window
APP = QApplication([])
MainFrame = MainWindow()
MainFrame.show()
sys.exit(APP.exec())