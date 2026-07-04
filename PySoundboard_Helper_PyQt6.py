import os, json, rich, re
from PyQt6.QtMultimedia import QMediaDevices
from AudioSystem_PyQt6 import *
def InitializeSettings():
    Values:dict = {}
    # add parameters for button sizes and stuff
    Defaults = {"AudioDevice":None, "Volume":8, "UseSystemTheme":True, "MaxRows":8, "Splash":True, "HandHeld":False, "DebugInfo":False}
    def writeNewJSONValues(update=False):
        if update:
            with open("Settings.json","r") as Dump:
                data = Dump.read()
        with open("Settings.json","w") as Dump:
            Dump.write(json.dumps(Defaults)) if not update else Dump.write(json.dumps(Defaults | json.loads(data)))
    def cleanJSONConfig():
        with open("Settings.json","r") as Dump:
            data:dict = json.loads(Dump.read())
        with open("Settings.json","w") as Dump:
            commonKeys = set(data) & set(Defaults)
            cleaned = {}
            for key in commonKeys:
                cleaned[key] = data.get(key)
            Dump.write(json.dumps(cleaned))
    # add checks for deprecated keys and remove them.
    # not really necessary, but i think it'd help make sure
    # that the json is clean from all changes ill make in the future.
    if os.path.exists("Settings.json"):
        # Check for missing Keys
        try:
            with open('Settings.json','r') as SettingsValue:
                Values = json.loads(SettingsValue.read())
                # Validate
                check_conf = list(Defaults.keys() - Values.keys())
                if len(check_conf) == 0:
                    rich.print('[PySoundboard] Validation: [b]Settings OK !')
                else:
                    raise KeyError(f"Missing Key/s: {check_conf}")
        except (json.decoder.JSONDecodeError, KeyError) as err:
            rich.print(f"\n[PySoundboard] Settings: {repr(err)}")
            writeNewJSONValues(update=True)
            return InitializeSettings()
        # Check for Deprecated keys
        try:
            with open('Settings.json','r') as SettingsValue:
                Values = json.loads(SettingsValue.read())
                check_conf = list(Values.keys() - Defaults.keys())
                if len(check_conf) == 0:
                    rich.print('[PySoundboard] Settings Cleaner: [b]Settings OK !')
                else:
                    raise KeyError(f"Unused Key/s: {check_conf}")
        except (json.decoder.JSONDecodeError, KeyError) as err:
            rich.print(f"\n[PySoundboard] Settings: {repr(err)}")
            cleanJSONConfig()
            return InitializeSettings()
    else:
        writeNewJSONValues()
        return InitializeSettings()
    return Values
        
def InitializeAudioSystem(Settings:dict):
    if Settings['AudioDevice'] is None:
        if os.name == 'nt': rich.print('\n[PySoundboard] VB-Audio VoiceMeeter/VB-Audio Virtual Cable [NOT FOUND]\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n')     
        else: rich.print('\n[PySoundboard] Using [System Default Output] !\n[PySoundboard] <Settings.json> "AudioDevice":None !\n')
    def _getDevice():
        for device in QMediaDevices.audioOutputs():
            if device.description() == Settings['AudioDevice']:
                return device
    return AudioManager(_getDevice(),{'audio':SoundType.AUDIO_MEDIA,'sound':SoundType.SOUND_EFFECT}, initVolume=Settings['Volume'])
def togglePlaybackStateAll(AudioSystem:AudioManager):
    pool = AudioSystem.audioPool['audio']
    for slot in pool:
        if not MediaLoaded.contains(slot.mediaStatus()): continue
        if slot.playbackState() == PlaybackStatus.PLAYING.value:
            AudioSystem.pauseSlot('audio',pool.index(slot))
        else:
            AudioSystem.playSlot('audio',pool.index(slot))
def togglePlaybackStateSlot(AudioSystem:AudioManager, slot):
    pool = AudioSystem.audioPool['audio']
    slotItem:AudioMedia = pool[slot]
    if slotItem.playbackState() == PlaybackStatus.PLAYING.value:
        AudioSystem.pauseSlot('audio',pool.index(slotItem))
    else:
        AudioSystem.playSlot('audio',pool.index(slotItem))
def GenerateSoundIndex(AudioSystem:AudioManager, path) -> dict:
    if not os.path.exists(path):
        rich.print(f'[yellow][PySoundboard] Checking Path: <{path}>[/yellow][red] Not Found[/red]')
        os.mkdir(path)
        rich.print(f'[yellow][PySoundboard] Creating Path: <{path}>[/yellow][green] Created[/green]')
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
        # AI Generated key= arg
        Index[each] = sorted(Index[each], key=lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)])
    # Return dict {tabName:[buttonName, playFunc]}
    return Index
