# Looks like PyQt6 has some sound capabilities, might re-write Soundboard_Backend to be fully PyQt
import PyQt6.QtMultimedia as QtM # Perhaps a new Backend..?
import time, os, json, xpfpath

global LoopState, LoopTextState
ComDispName = []
LoopTextState, LoopState,  = "  Looping Disabled", 0
SpammingState, SpammingTextState = 0, 'Multi-Mode OFF'
AudioFolder = xpfpath.xpfp(".\\SoundFiles")
AudioFilesIndex:list = []

def InitializeSettings():
    global Settings
    time.sleep(1)
    print('check existance of Settings.json')
    if os.path.exists("Settings.json") == True:
        print('test reading')
        try:
            print('reading')
            with open('Settings.json','r') as SettingsValue:
                Settings = json.loads(SettingsValue.read())
        except Exception as Err:
            print(f"\nError Occured: {Err}\n")
            os.remove("Settings.json")
            print("settings.json is being reset")
            InitializeSettings()
            print("settings.json reset complete")
    else:
        print(f'existance check failed: {os.path.exists("Settings.json")}')
        x = {"AudioDevice":"CABLE Input (VB-Audio Virtual Cable)","Volume":"10","MaxRows":"8","Splash":"1"}
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
        
    SoundButton(r"..\startup.wav").Play() #try to look for a way to make this not be bound to only .wav files for startup sound!
    
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

class SoundButton:
    def __init__(self, AudioFile: str) -> None:
        self.AudioFile = AudioFile
    def Play(self):
        global Title
        Title = f"'{self.AudioFile}'" # Currently playing Window Title
        # if SpammingState == 1 and mixer.music.get_pos()/1000 > 0:
        #     Sound = mixer.Sound(xpfpath.xpfp(AudioFolder+"\\"+self.AudioFile))
        #     Sound.set_volume(float(Settings['Volume'])/100)
        #     Sound.play()
        # else:
        #     mixer.fadeout(0) # fix multi-mode long sounds not stopping when multi mode is disabled
        #     mixer.music.unload()
        #     mixer.music.load(xpfpath.xpfp(AudioFolder+"\\"+self.AudioFile))
        #     mixer.music.play(loops=LoopState)

# Recursive... May need to tweak a little bit
def GenerateSoundIndex(path):
    print(f'Scanning [{path}]')
    try:
        FolderContents = os.scandir(path)
    except:
        os.mkdir(AudioFolder)
        FolderContents = os.scandir(path)
    for Entry in FolderContents:
        # time.sleep(0.015625)
        if Entry.is_file():
            name:str = str(Entry.name.rsplit(".",1)[0]) # omit file extension.
            folder:str = str(path).rsplit(f"{'\\' if os.name=='nt' else '/'}",1)[1] # Get actual folder where file is located.
            # add into an uncategorized TAB
            AudioFilesIndex.append([folder,name,SoundButton(Entry.path).Play])
        else:
            GenerateSoundIndex(Entry.path)
    return AudioFilesIndex
    # try:
    #     Files = os.scandir(PATH)
    # except Exception as ERR:
    #     # when PyInstaller is used, CLI is not visible. use a window pop up instead/In-app Label!!
    #     print(f'You do not have Sounds yet, SoundFiles Folder has been created!\nJust drag and drop your audio files in {xpfpath.xpfp(".\\SoundFiles")} folder and run the Program!')
    #     os.mkdir('SoundFiles')
    #     time.sleep(2)

InitializeSettings()
InitializeAudioSystem()
ComDispName = GenerateSoundIndex(AudioFolder)
for _ in ComDispName:
    print(_)
time.sleep(1)