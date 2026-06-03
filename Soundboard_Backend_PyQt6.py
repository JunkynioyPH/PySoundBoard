import time, os, json, xpfpath, rich
from PyQt6.QtMultimedia import QMediaDevices
from rich import pretty
from AudioSystem_PyQt6 import *
pretty.install()

Settings:dict = {}
# Settings:dict
LoopTextState, GlobalLoopState,  = "Looping ALL OFF", 0
SpammingState, SpammingTextState = 0, 'Multi-Mode OFF'
AudioFolder = xpfpath.xpfp(".\\SoundFiles")
Title = ''
SyncSpeedState:bool = True
SelectedSlot:int = 0

def InitializeSettings():
    global Settings
    # add parameters for button sizes and stuff
    Defaults = {"AudioDevice":None,"Volume":8,"UseSystemTheme":True,"MaxRows":8,"Splash":True, "SteamDeck":False}
    def writeNewJSONValues(update=False):
        if update:
            with open("Settings.json","r") as Dump:
                data = Dump.read()
        with open("Settings.json","w") as Dump:
            Dump.write(json.dumps(Defaults)) if not update else Dump.write(json.dumps(Defaults | json.loads(data)))
    
    # add checks for deprecated keys and remove them.
    # not really necessary, but i think it'd help make sure
    # that the json is clean from all changes ill make in the future.
    if os.path.exists("Settings.json"):
        # Check for missing Keys
        try:
            with open('Settings.json','r') as SettingsValue:
                Settings = json.loads(SettingsValue.read())
                # Validate
                check_conf = list(Defaults.keys() - Settings.keys())
                if len(check_conf) == 0:
                    rich.print('[PySoundboard] [b]Settings OK !')
                else:
                    raise KeyError(f"Missing Key/s: {check_conf}")
        except (json.decoder.JSONDecodeError, KeyError) as err:
            rich.print(f"\n[PySoundboard] Settings: {repr(err)}")
            writeNewJSONValues(update=True)
            InitializeSettings()
        # Check for Deprecated keys
        try:
            ...
        except (json.decoder.JSONDecodeError, KeyError) as err:
            rich.print(f"\n[PySoundboard] Settings: {repr(err)}")
            print('OMIT OLD KEYS') # STUB
            InitializeSettings()
    else:
        writeNewJSONValues()
        InitializeSettings()
        
def InitializeAudioSystem():
    if Settings['AudioDevice'] is None:
        rich.print('\n[PySoundboard] VB-Audio VoiceMeeter/VB-Audio Virtual Cable [NOT FOUND]\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n') if os.name == 'nt' else rich.print('\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n')     
    def _getDevice():
        for device in QMediaDevices.audioOutputs():
            if device.description() == Settings['AudioDevice']:
                return device
    return AudioManager(_getDevice(),{'audio':SoundType.AUDIO_MEDIA}, initVolume=Settings['Volume'])

def togglePlaybackStateAll(AudioSystem:AudioManager):
    pool = AudioSystem.audioPool['audio']
    for slot in pool:
        if not slot.mediaStatus() in MediaLoaded: continue
        rich.print(f"[PySoundboard] [yellow]TogglePlayback Status[/yellow]: Set {slot} to ",end='')
        if slot.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            rich.print(f"[b]{PlaybackStatus.PAUSED}[/b]")
            AudioSystem.pauseSlot('audio',pool.index(slot))
        else:
            rich.print(f"[b]{PlaybackStatus.PLAYING}[/b]")
            AudioSystem.playSlot('audio',pool.index(slot))
       
# might change 
def ToggleLoopSync(AudioSystem:AudioManager):
    global GlobalLoopState, LoopTextState
    if GlobalLoopState == 0:
        LoopTextState, GlobalLoopState = "Looping ALL ON", -1
    else:
        LoopTextState, GlobalLoopState = "Looping ALL OFF", 0
    # AudioSystem.toggleLooping('audio') ### WILL BREAK ... ?
    for slot in range(0,AudioSystem.audioPoolSize):
        AudioSystem.toggleLoopAudioMediaSlot('audio', slot)
        
def ToggleSpamming():
    global SpammingState, SpammingTextState
    if SpammingState == 0:
        SpammingState, SpammingTextState = 1, "Multi-Mode ON"
        rich.print('[PySoundboard] Toggle MultiMode: [green b]True[/green b]')

    else:
        SpammingState, SpammingTextState = 0, "Multi-Mode OFF"
        rich.print('[PySoundboard] Toggle MultiMode: [red b]False[/red b]')

def GenerateSoundIndex(AudioSystem:AudioManager, path) -> dict:
    SubFoldersIndex:list[os.DirEntry] = []
    if not os.path.exists(path):
        rich.print(f'[yellow][PySoundboard] Checking: <{path}>[/yellow][red] Not Found[/red]')
        os.mkdir(AudioFolder)
        rich.print(f'[yellow][PySoundboard] Checking: <{path}>[/yellow][green] Created[/green]')
        
    # Scan Root ./SoundFiles
    rich.print(f'[yellow][PySoundboard] Scanning [{path}][/yellow]')
    RootFolderContents = os.scandir(path)
    for File in RootFolderContents:
        AudioSystem.addIndex(SoundType.AUDIO_MEDIA,f'{xpfpath.xpfp(File.path)}') if File.is_file() else SubFoldersIndex.append(File.path)
    # Scan Subfolders
    for Folder in SubFoldersIndex:
        rich.print(f'[blue][PySoundboard] Scanning [{Folder}][/blue]')
        SubFolderContents = os.scandir(Folder)
        for File in SubFolderContents:
            AudioSystem.addIndex(SoundType.AUDIO_MEDIA,f'{xpfpath.xpfp(File.path)}') if File.is_file() else SubFoldersIndex.append(File.path)
    # idk but i did anyways
    del RootFolderContents, SubFoldersIndex
    
    # create index for the GUI generator
    Index:dict[str, list[list[str]]] = {}
    for each in AudioSystem.audioIndex[SoundType.AUDIO_MEDIA]:
        # get path
        filepath:str = os.path.split(AudioSystem.audioIndex[SoundType.AUDIO_MEDIA].get(each))[0]
        
        # split @ / or \\ to get folder names
        parentdir:list[str] = filepath.split('/' if os.name!='nt' else "\\")
        
        # Readable
        # if len is < 3, then use an index before 2
        # this caused some issues when i did A:\\ as base root, index out of range.
        # might fix some point :P
        tabName, buttonName, playFunc = parentdir[2 if len(parentdir) < 4 else 3], each, SoundFile(each, AudioSystem).Play
        # print(tabName)
        button = [buttonName,playFunc]
        
        # create if it no exist pls thx
        if not Index.get(tabName): Index[tabName] = []
        
        # append
        Index.get(tabName).append(button)
        
        rich.print(f'[GUI] Button Indexing: <Tab_[blue bold]{tabName}[/blue bold]> << {button} ')
        
    # sorting
    for each in Index:
        rich.print(f"[GUI] Button Sorting: <Tab_[yellow bold]{each}[/yellow bold]>")
        Index[each] = sorted(Index[each])
        
    # Return dict {tabName:[buttonName, playFunc]}
    return Index

# PyQt Sound System
class SoundFile:
    def __init__(self, filepath:str, AudioSystem:AudioManager):
        self.file = filepath # Its keyName on dictionary
        self.AudioSystem = AudioSystem
    def Play(self):
        global Title
        Title = f"'{self.file}'"
        self.AudioSystem.loadAudioMedia('audio', self.file) if SpammingState == 1 else self.AudioSystem.loadAudioMedia('audio',self.file, SelectedSlot)
        self.AudioSystem.playAll() if SpammingState == 1 else self.AudioSystem.playSlot("audio", SelectedSlot)
        rich.print(f" - {GlobalLoopState}/{SpammingState}"+LoopTextState+"/"+SpammingTextState)
    def __repr__(self):
        return self.file
