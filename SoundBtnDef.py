# from AudioDef import *
from pygame import mixer
import time, os

# Structure ["DisplayName,AD.DisplayName"]

ComDispName = []

LoopTextState, LoopState = "  No   Looping", 0
AudioFolder = r".\SoundFiles"
AudioFilesIndex = []

def ToggleLoop():
    global LoopState, LoopTextState
    if LoopState == 0:
        LoopTextState, LoopState = "  Yes Looping", -1
    else:
        LoopTextState, LoopState = "  No   Looping", 0

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
        try:
            AudioPath = self.AudioFile # for the window title
            mixer.music.unload()
            mixer.music.load(AudioFolder+"\\"+self.AudioFile)
            mixer.music.play(loops=LoopState)
        except Exception as Err:
            PrintErr('class.SoundButton.Play()',Err)

def ScanDir(PATH):
    print('Scanning for AudioFiles...')
    time.sleep(1)
    Files = os.scandir(PATH)
    for Entry in Files:
        # time.sleep(0.015625)
        if Entry.is_file():
            AudioFilesIndex.append(Entry.name)
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
