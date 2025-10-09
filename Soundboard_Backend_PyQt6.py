import time, os, json, xpfpath, rich
from PyQt6.QtMultimedia import QMediaDevices
from rich import pretty
pretty.install()

# Use standard
if os.name=='nt': import AudioSystem_PyQt6 as AS_PYQT6 
# Use Linux Pipewire fix
else: import AudSys_LinuxPatch as AS_PYQT6

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
            rich.print(f"\n[PySoundboard] Error: {Err}\n")
            os.remove("Settings.json")
            rich.print("[PySoundboard] settings.json is being reset")
            InitializeSettings()
            rich.print("[PySoundboard] settings.json reset complete")
    else:
        x = {"AudioDevice":None,"Volume":10,"MaxRows":"8","Splash":"1"}
        with open("Settings.json","a") as DefaultSettingsDump:
            DefaultSettingsDump.write(json.dumps(x))
        InitializeSettings()
        
def InitializeAudioSystem():
    if Settings['AudioDevice'] is None:
        rich.print('\n[PySoundboard] VB-Audio VoiceMeeter/VB-Audio Virtual Cable [NOT FOUND]\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n') if os.name == 'nt' else rich.print('\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n')     
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

def GenerateSoundIndex(path) -> tuple:
    SubFoldersIndex:list[os.DirEntry] = []
    if not os.path.exists(path):
        rich.print(f'[yellow][PySoundboard] Checking: <{path}>[/yellow][red] Not Found[/red]')
        os.mkdir(AudioFolder)
        rich.print(f'[yellow][PySoundboard] Checking: <{path}>[/yellow][green] Created[/green]')
        
    rich.print(f'[yellow][PySoundboard] Scanning [{path}][/yellow]')
    RootFolderContents = os.scandir(path)
    
    # Scan Root ./SoundFiles
    for File in RootFolderContents:
        AudioSystem.addIndex('audio',f'{xpfpath.xpfp(File.path)}') if File.is_file() else SubFoldersIndex.append(File.path)
    # Scan Subfolders
    for Folder in SubFoldersIndex:
        rich.print(f'[blue][PySoundboard] Scanning [{Folder}][/blue]')
        SubFolderContents = os.scandir(Folder)
        for File in SubFolderContents:
            AudioSystem.addIndex('audio',f'{xpfpath.xpfp(File.path)}') if File.is_file() else SubFoldersIndex.append(File.path)
    # idk but i did anyways
    del RootFolderContents, SubFoldersIndex
    
    # create index for the GUI generator
    Index:list = []
    for each in AudioSystem.audioIndex['audio']:
        _a:str = os.path.split(AudioSystem.audioIndex['audio'].get(each))[0] # get path
        _b:list[str] = _a.split('/' if os.name!='nt' else "\\") # split @ / or \\
            
        # if len is < 3, then use an index before 2
        _ = [_b[1 if len(_b) < 3 else 2],each,SoundFile(each).Play]
        
        # append
        Index.append(_)
        rich.print(f'[GUI] Button Indexing: {_}')

    # Return (TabName, ButtonName, PlayFunction)
    return tuple(sorted(Index))

# PyQt Sound System
class SoundFile:
    def __init__(self, filepath:str):
        self.file = filepath # Its keyName on dictionary
    def Play(self):
        global Title
        Title = f"'{self.file}'"
        AudioSystem.play('audio',self.file)
        rich.print(f" - {LoopState}/{SpammingState}"+LoopTextState+"/"+SpammingTextState)
    def __repr__(self):
        return self.file


InitializeSettings()
AudioSystem = InitializeAudioSystem()
ComDispName = GenerateSoundIndex(AudioFolder)
time.sleep(1)