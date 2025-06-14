# Looks like PyQt6 has some sound capabilities, might re-write Soundboard_Backend to be fully PyQt
import time, os, json, xpfpath
import AudioSystem_PyQt6 #as mixer

ComDispName = []
LoopTextState, LoopState,  = "  Looping Disabled", 0
SpammingState, SpammingTextState = 0, 'Multi-Mode OFF'
AudioFolder = xpfpath.xpfp(".\\SoundFiles")
AudioFilesIndex:list = []
SubFoldersIndex:list = []

def InitializeSettings():
    global Settings
    time.sleep(1)
    if os.path.exists("Settings.json") == True:
        try:
            with open('Settings.json','r') as SettingsValue:
                Settings = json.loads(SettingsValue.read())
        except Exception as Err:
            print(f"\nError Occured: {Err}\n")
            os.remove("Settings.json")
            print("settings.json is being reset")
            InitializeSettings()
            print("settings.json reset complete")
    else:
        x = {"AudioDevice":None,"Volume":"10","MaxRows":"8","Splash":"1"}
        with open("Settings.json","a") as DefaultSettingsDump:
            DefaultSettingsDump.write(json.dumps(x))
        InitializeSettings()
def InitializeAudioSystem():
    if Settings['AudioDevice'] is None:
        print('\nVB-Audio VoiceMeeter/VB-Audio Virtual Cable [NOT FOUND]\nUsing [System Default Output] !\n[Settings.json] "AudioDevice":None !\n') if os.name == 'nt' else print('\nUsing [System Default Output] !\n[Settings.json] "AudioDevice":None !\n')
    # try:
    #     mixer.pre_init(devicename=Settings["AudioDevice"])
    #     mixer.init()
    # except Exception as err:
    #     print('\n???? System Defaulting!')
    #     mixer.pre_init(devicename=None)
    #     mixer.init()
    #     UpdateSettings('AudioDevice',None)
    # mixer.music.set_volume(float(Settings['Volume'])/100)
        
    SoundFile("../startup.wav").Play() #try to look for a way to make this not be bound to only .wav files for startup sound!
    
## These 2 Functions ar enot available Built-in on PyQt6, Will have to Create it from scratch.
def ToggleLoop():
    global LoopState, LoopTextState
    if LoopState == 0:
        LoopTextState, LoopState = "  Looping  Enabled", -1
    else:
        LoopTextState, LoopState = "  Looping Disabled", 0
def ToggleSpamming():
    global SpammingState, SpammingTextState
    if SpammingState == 0:
        SpammingState, SpammingTextState = 1, "Multi-Mode  ON"
    else:
        SpammingState, SpammingTextState = 0, "Multi-Mode OFF"

# It now only scans ./SoundFiles and its folders, Not Recurseive!
# no more nested folders
def GenerateSoundIndex(path):
    print(f'Scanning [{path}]')
    try:
        FolderContents = os.scandir(path)
    except:
        os.mkdir(AudioFolder)
        FolderContents = os.scandir(path)
    def add(_:str):
        name:str = str(_.name.rsplit(".",1)[0]) # omit file extension.
        folder:str = str(_.path).rsplit(f"{'\\' if os.name=='nt' else '/'}",2)[1] # Get actual folder where file is located.
        AudioFilesIndex.append([folder,name,SoundFile(Entry.path).Play])
    # scan "Root" ./SoundFiles Folder for files and Folders
    for Entry in FolderContents:
        add(Entry) if Entry.is_file() else SubFoldersIndex.append(Entry.path)
    # scan "SubFolders" for files and add()
    for folder in SubFoldersIndex:
        FolderContents = os.scandir(folder)
        for Entry in FolderContents:
            add(Entry) if Entry.is_file() else ''
    return AudioFilesIndex

# PyQt Sound System
class SoundFile:
    def __init__(self, filepath:str):
        # super().__init__()
        self.file = filepath
    def Play(self):
        global Title
        Title = f"'{self.file}'"
        print(self.file+f" - {LoopState}/{SpammingState}"+LoopTextState+"/"+SpammingTextState)
        pass

# For refrerence down the line
# class SoundButton:
#     def __init__(self, AudioFile: str) -> None:
#         self.AudioFile = AudioFile

#     def Play(self):
#         global LoopState, LoopTextState, AudioPath, Title
#         AudioPath = self.AudioFile # for the window title
#         Title = f"'{AudioPath}'"
#         if SpammingState == 1 and mixer.music.get_pos()/1000 > 0:
#             Sound = mixer.Sound(xpfpath.xpfp(AudioFolder+"\\"+self.AudioFile))
#             Sound.set_volume(float(Settings['Volume'])/100)
#             Sound.play()
#         else:
#             mixer.fadeout(0) # fix multi-mode long sounds not stopping when multi mode is disabled
#             mixer.music.unload()
#             mixer.music.load(xpfpath.xpfp(AudioFolder+"\\"+self.AudioFile))
#             mixer.music.play(loops=LoopState)


InitializeSettings()
InitializeAudioSystem()
ComDispName = GenerateSoundIndex(AudioFolder)
for _ in ComDispName:
    print(_)
time.sleep(1)