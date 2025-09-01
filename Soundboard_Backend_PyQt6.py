# Looks like PyQt6 has some sound capabilities, might re-write Soundboard_Backend to be fully PyQt
import time, os, json, xpfpath
import AudioSystem_PyQt6 as AS_PYQT6
from PyQt6.QtMultimedia import QMediaDevices

ComDispName = []
LoopTextState, LoopState,  = "  Looping Disabled", 0
SpammingState, SpammingTextState = 0, 'Multi-Mode OFF'
AudioFolder = xpfpath.xpfp(".\\SoundFiles")
Title = ''

def InitializeSettings():
    global Settings
    if os.path.exists("Settings.json") == True:
        try:
            with open('Settings.json','r') as SettingsValue:
                Settings = json.loads(SettingsValue.read())
        except Exception as Err:
            print(f"\n[PySoundboard] Error: {Err}\n")
            os.remove("Settings.json")
            print("[PySoundboard] settings.json is being reset")
            InitializeSettings()
            print("[PySoundboard] settings.json reset complete")
    else:
        x = {"AudioDevice":None,"Volume":10,"MaxRows":"8","Splash":"1"}
        with open("Settings.json","a") as DefaultSettingsDump:
            DefaultSettingsDump.write(json.dumps(x))
        InitializeSettings()
        
def InitializeAudioSystem():
    if Settings['AudioDevice'] is None:
        print('\n[PySoundboard] VB-Audio VoiceMeeter/VB-Audio Virtual Cable [NOT FOUND]\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n') if os.name == 'nt' else print('\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n')     
    def _getDevice():
        for device in QMediaDevices.audioOutputs():
            if device.description() == Settings['AudioDevice']:
                return device
    return AS_PYQT6.AudioManager(_getDevice(), Settings['Volume'])
    
def ToggleLoop():
    global LoopState, LoopTextState
    if LoopState == 0:
        LoopTextState, LoopState = "  Looping  Enabled", -1
        AudioSystem.toggleState('audio','loop')
    else:
        LoopTextState, LoopState = "  Looping Disabled", 0
        AudioSystem.toggleState('audio','loop')
def ToggleSpamming():
    global SpammingState, SpammingTextState
    if SpammingState == 0:
        SpammingState, SpammingTextState = 1, "Multi-Mode  ON"
        AudioSystem.toggleState('audio','multi')
    else:
        SpammingState, SpammingTextState = 0, "Multi-Mode OFF"
        AudioSystem.toggleState('audio','multi')

# It now only scans ./SoundFiles and its folders, Not Recursive!
# no more nested folders
def GenerateSoundIndex(path) -> tuple:
    AudioFilesIndex:list = []
    SubFoldersIndex:list = []
    print(f'Scanning [{path}]')
    try:
        FolderContents = os.scandir(path)
    except:
        os.mkdir(AudioFolder)
        FolderContents = os.scandir(path)
    def add(_):
        name:str = str(_.name.rsplit(".",1)[0]) # omit file extension.
        folder:str = str(_.path).rsplit(f"{'\\' if os.name=='nt' else '/'}",2)[1] # Get actual folder where file is located.
        AudioFilesIndex.append([folder,name,SoundFile(Entry.path).Play])
        print(f"[GUI] [Tab: {folder}] (Button: {name})")
    # scan "Root" ./SoundFiles Folder for files and Folders
    for Entry in FolderContents:
        add(Entry) if Entry.is_file() else SubFoldersIndex.append(Entry.path)
    # scan "SubFolders" for files and add()
    for folder in SubFoldersIndex:
        FolderContents = os.scandir(folder)
        for Entry in FolderContents:
            add(Entry) if Entry.is_file() else ''
    return tuple(AudioFilesIndex)

# PyQt Sound System
class SoundFile:
    def __init__(self, filepath:str):
        # super().__init__()
        self.file = filepath
        AudioSystem.load('audio',self.file)
    def Play(self):
        global Title
        Title = f"'{self.file}'"
        AudioSystem.play('audio',os.path.splitext(os.path.basename(self.file))[0])
        print(f" - {LoopState}/{SpammingState}"+LoopTextState+"/"+SpammingTextState)
    def __repr__(self):
        return self.file


InitializeSettings()
##
# Double AudioSystem into "MicAudioSystem" and "HostAudioSystem"
# as a fix for linux-pipewire, when my mic HyperXDuocast and my Starmatisse hate each other when Firefox is playing audio.
# make it so it only applies to linux "os.name == posix"
##
AudioSystem = InitializeAudioSystem()
ComDispName = GenerateSoundIndex(AudioFolder)
time.sleep(1)