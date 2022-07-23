from pygame import mixer
import os, time

LoopTextState, LoopState = "  No   Looping", 0
AudioFolder = ".\SoundFiles"
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

def Play(AudioFile):
    global LoopState, LoopTextState, AudioPath
    try:
        AudioPath = AudioFile # for the window title
        mixer.music.unload()
        mixer.music.load(AudioFolder+"\\"+AudioFile)
        mixer.music.play(loops=LoopState)
    except Exception as Err:
        PrintErr('AudioDef.Play()',Err)

def ScanDir(PATH):
    Files = os.scandir(PATH)
    for Entry in Files:
        # time.sleep(0.015625)
        if Entry.is_file():
            AudioFilesIndex.append(Entry.name)
    print(AudioFilesIndex)

os.system('cls' if os.name=='nt' else 'clear')
print('## FILES FOUND ##\n')
ScanDir(AudioFolder)
print('\n## FILES FOUND ##')
time.sleep(2)
