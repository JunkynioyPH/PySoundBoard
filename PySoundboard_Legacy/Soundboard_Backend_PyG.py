from pygame import mixer
import time, os, json, xpfpath

def InitializeSettings():
    global Settings
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
InitializeSettings()
# Structure ["DisplayName,AD.DisplayName"]

ComDispName = []

LoopTextState, LoopState,  = "  Looping Disabled", 0
SpammingState, SpammingTextState = 0, 'Multi-Mode OFF'
AudioFolder = xpfpath.xpfp(".\\SoundFiles")
AudioFilesIndex:list = []

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

def PrintErr(Where,Err):
    print("\n=====================================")
    print("Error During "+Where)
    print(Err)
    print("=====================================")

# POV: You learned about classes and the ability to create different instance of the same object
class SoundButton:
    def __init__(self, AudioFile: str) -> None:
        self.AudioFile = AudioFile

    def Play(self):
        global LoopState, LoopTextState, AudioPath, Title
        AudioPath = self.AudioFile # for the window title
        Title = f"'{AudioPath}'"
        if SpammingState == 1 and mixer.music.get_pos()/1000 > 0:
            Sound = mixer.Sound(xpfpath.xpfp(AudioFolder+"\\"+self.AudioFile))
            Sound.set_volume(float(Settings['Volume'])/100)
            Sound.play()
        else:
            mixer.fadeout(0) # fix multi-mode long sounds not stopping when multi mode is disabled
            mixer.music.unload()
            mixer.music.load(xpfpath.xpfp(AudioFolder+"\\"+self.AudioFile))
            mixer.music.play(loops=LoopState)

# POV: you dont have to manually make the buttons and functions anymore
def ScanDir(PATH):
    print('Scanning for AudioFiles...')
    time.sleep(1)
    try:
        Files = os.scandir(PATH)
    except Exception as ERR:
        PrintErr('SoundBtnDef.ScanDir()',ERR)
        print('You do not have Sounds yet, SoundFiles Folder has been created!\nJust drag and drop your audio files in .\\SoundFiles folder and run the Program!')
        os.mkdir('SoundFiles')
        # os.system('mkdir .\\SoundFiles')
        time.sleep(2)
    for Entry in Files:
        # time.sleep(0.015625)
        if Entry.is_file():
            AudioFilesIndex.append(Entry.name) # look into os.scandir() later to make the code below more 'better''
    # print(f"Full Index:\n{AudioFilesIndex}")
    for Files in AudioFilesIndex:
        x, y = [], ""
        for letter in Files:
            if letter == ".":
                break
            else:
                x += letter
        y += "".join(x)
         # print(y)
        Sound: SoundButton = SoundButton(f"{Files}")
        ComDispName.append([f"{y}", Sound.Play])
        print([f"{y}", Sound.Play])
        # time.sleep(0.0015625)
    # else:
    #     print('Sounds List Compiled.')

os.system('cls' if os.name=='nt' else 'clear')
ScanDir(AudioFolder)
time.sleep(1)
