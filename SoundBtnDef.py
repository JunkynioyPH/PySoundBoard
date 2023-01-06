# from AudioDef import *
from pygame import mixer
from pathlib import Path
import time, os, json

def InitializeSettings():
    global Settings
    if Path("Settings.json").exists() == True:
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
        x = {"AudioDevice":"CABLE Input (VB-Audio Virtual Cable)","Volume":"10","MaxRows":"3","Splash":"1"}
        DefSettingsDump = open("Settings.json","a")
        print("settings.json [Created]")
        DefSettingsDump.write(json.dumps(x))
        print("settings.json [Accessed]")
        DefSettingsDump.close()
        print("settings.json [Closed]")
        InitializeSettings()
        print("Rerun InitializeSettings")
InitializeSettings()
# Structure ["DisplayName,AD.DisplayName"]

ComDispName = []

LoopTextState, LoopState,  = "  No   Looping", 0
SpammingState, SpammingTextState = 0, '  No   Spamming'
AudioFolder = r".\SoundFiles"
AudioFilesIndex = []

def ToggleLoop():
    global LoopState, LoopTextState
    if LoopState == 0:
        LoopTextState, LoopState = "  Yes Looping", -1
    else:
        LoopTextState, LoopState = "  No   Looping", 0

def ToggleSpamming():
    global SpammingState, SpammingTextState
    if SpammingState == 0:
        SpammingState, SpammingTextState = 1, "  Yes Spamming"
    else:
        SpammingState, SpammingTextState = 0, "  No   Spamming"

def PrintErr(Where,Err):
    print("\n=====================================")
    print("Error During "+Where)
    print(Err)
    print("=====================================")


# might move to class
class SoundButton:
    def __init__(self, AudioFile: str) -> None:
        self.AudioFile = AudioFile

    def Play(self):
        global LoopState, LoopTextState, AudioPath
        if SpammingState == 1 and mixer.music.get_pos()/1000 > 0:
            AudioPath = self.AudioFile # for the window title
            Sound = mixer.Sound(AudioFolder+"\\"+self.AudioFile)
            Sound.set_volume(float(Settings['Volume'])/100) ## DOES NOT UPDATE WHEN VOLUME IS CHANGED DURIHNG RUNTIME.
            Sound.play()
        else:
            AudioPath = self.AudioFile # for the window title
            mixer.music.unload()
            mixer.music.load(AudioFolder+"\\"+self.AudioFile)
            mixer.music.play(loops=LoopState)

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


os.system('cls' if os.name=='nt' else 'clear')
ScanDir(AudioFolder)
time.sleep(1)
