import os, json, rich
from PyQt6.QtMultimedia import QMediaDevices
from AudioSystem_PyQt6 import *
def InitializeSettings():
    Settings:dict = {}
    # add parameters for button sizes and stuff
    Defaults = {"AudioDevice":None,"Volume":8,"UseSystemTheme":True,"MaxRows":8,"Splash":True, "HandHeld":False}
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
    return Settings
        
def InitializeAudioSystem(Settings:dict):
    if Settings['AudioDevice'] is None:
        if os.name == 'nt': rich.print('\n[PySoundboard] VB-Audio VoiceMeeter/VB-Audio Virtual Cable [NOT FOUND]\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n')     
        else: rich.print('\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n')
    def _getDevice():
        for device in QMediaDevices.audioOutputs():
            if device.description() == Settings['AudioDevice']:
                return device
    return AudioManager(_getDevice(),{'audio':SoundType.AUDIO_MEDIA}, initVolume=Settings['Volume'])
def togglePlaybackStateAll(AudioSystem:AudioManager):
    pool = AudioSystem.audioPool['audio']
    for slot in pool:
        if not MediaLoaded.contains(slot.mediaStatus()): continue
        rich.print(f"[PySoundboard] [yellow]TogglePlayback Status[/yellow]: Set {slot} to ",end='')
        if slot.playbackState() == PlaybackStatus.PLAYING.value:
            rich.print(f"[b]{PlaybackStatus.PAUSED}[/b]")
            AudioSystem.pauseSlot('audio',pool.index(slot))
        else:
            rich.print(f"[b]{PlaybackStatus.PLAYING}[/b]")
            AudioSystem.playSlot('audio',pool.index(slot))
def togglePlaybackStateSlot(AudioSystem:AudioManager, slot):
    pool = AudioSystem.audioPool['audio']
    slotItem:AudioMedia = pool[slot]
    rich.print(f"[PySoundboard] [yellow]TogglePlayback Status[/yellow]: Set {slotItem} to ",end='')
    if slotItem.playbackState() == PlaybackStatus.PLAYING.value:
        rich.print(f"[b]{PlaybackStatus.PAUSED}[/b]")
        AudioSystem.pauseSlot('audio',pool.index(slotItem))
    else:
        rich.print(f"[b]{PlaybackStatus.PLAYING}[/b]")
        AudioSystem.playSlot('audio',pool.index(slotItem))
def GenerateSoundIndex(AudioSystem:AudioManager, path) -> dict:
    if not os.path.exists(path):
        rich.print(f'[yellow][PySoundboard] Checking: <{path}>[/yellow][red] Not Found[/red]')
        os.mkdir(path)
        rich.print(f'[yellow][PySoundboard] Checking: <{path}>[/yellow][green] Created[/green]')
    # Scan Root ./SoundFiles
    rich.print(f'[yellow][PySoundboard] Scanning [{path}][/yellow]')
    RootFolderContents = os.scandir(path)
    SubFoldersIndex:list[os.DirEntry] = []
    Index:dict[str, list[list[str]]] = {}
    def _addSound(tabname:str, File:os.DirEntry):
        if not Index.get(tabname):
            Index[tabname] = []
        AudioSystem.addIndex(SoundType.AUDIO_MEDIA, File.path)
        Index[tabname].append(list(AudioSystem.audioIndex[SoundType.AUDIO_MEDIA])[-1])
    # Scan root, if root has sound files, create new tab
    for File in RootFolderContents:
        if File.is_file():
            _addSound('SoundFiles', File)
        else:
            SubFoldersIndex.append(File)
    # Scan Subfolders
    for Folder in SubFoldersIndex:
        rich.print(f'[blue][PySoundboard] Scanning [{Folder}][/blue]')
        for File in os.scandir(Folder):
            if File.is_file():
                _addSound(Folder.name, File)
    # idk but i did anyways
    del RootFolderContents, SubFoldersIndex
    # sorting
    # need to implement better sorting.
    for each in Index:
        rich.print(f"[PySoundboard] [cyan]Button Sorting:[/cyan] <Tab_[yellow bold]{each}[/yellow bold]>")
        Index[each] = sorted(Index[each])
    # Return dict {tabName:[buttonName, playFunc]}
    return Index
