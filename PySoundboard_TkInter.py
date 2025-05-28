from tkinter import *
from tkinter import ttk
from pygame import mixer
import time, json, os
import SoundBtnDef as SD

# Console splash
def splash():
    os.system('cls' if os.name=='nt' else 'clear')
    os.system('title PySoundBoard Backend' if os.name=='nt' else 'echo PySoundboard Backend')
    print('''

    ██████╗ ██╗   ██╗███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██████╗  ██████╗  █████╗ ██████╗ ██████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗ T
    ██████╔╝ ╚████╔╝ ███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║ K
    ██╔═══╝   ╚██╔╝  ╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║ I
    ██║        ██║   ███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
                        Written By : @Junkynioy - https://github.com/JunkynioyPH
    ''')
splash()

# Preliminary preparations
root = Tk()

DefaultValSettings = ["CABLE Input (VB-Audio Virtual Cable)","VoiceMeeter Input (VB-Audio VoiceMeeter VAIO)",None]

# Essential Values
AudioDevice, Vol, SongPos = StringVar(), StringVar(), StringVar()
SongPos.set('0')

LoopState, SpammingState = StringVar(), StringVar()

# The sweet dark mode
try:
    from ttkthemes import ThemedStyle
    style = ThemedStyle(root)
    style.set_theme("equilux")
    # Change the Font of the program
    ttk.Style().configure(".",font=('Trebuchet MS Bold', 8), foreground='white')
    print('ttkthemes found! Used Dark Theme!')
except Exception as Err:
    print('')
    print(Err)
    print("\nError while applying themes :","Using fallback!")
    # Change the Font of the program
    ttk.Style().configure(".",font=('Trebuchet MS Bold', 8))

# Cointainers

# Top Header
header = ttk.Frame(root, relief=RAISED, borderwidth=4)
header.grid(column=0, row=0, sticky=(N, S,W, E))

headercenter = ttk.Frame(root)
headercenter.grid(padx=5, pady=8, column=0, row=0, sticky=(N, S))

headercontent = ttk.Frame(headercenter, relief=SUNKEN, borderwidth=2)
headercontent.grid(column=0, row=0, sticky=N)

# Bottom Body
mframe = ttk.Frame(root, relief=GROOVE, borderwidth=2)
mframe.grid(column=0, row=1, sticky=(N, W, E, S))

# Controls
controls = ttk.Frame(headercenter, relief=SUNKEN, borderwidth=2)
controls.grid(padx=10, pady=2, column=0, row=1, sticky=(N, S))

controlcontent = ttk.Frame(controls, relief=SUNKEN, borderwidth=2)
controlcontent.grid(column=1, row=1, sticky=(N, S))

controllabel = ttk.Frame(controls, relief=RAISED, borderwidth=2)
controllabel.grid(column=1, row=0, sticky=(N, W, E, S))

# Sound Buttons
soundboard = ttk.Frame(mframe, relief=SUNKEN, borderwidth=2)
soundboard.grid(padx=5, pady=5,column=1, row=1, sticky=(N, S))

soundbuttons = ttk.Frame(soundboard, relief=SUNKEN, borderwidth=2)
soundbuttons.grid(column=1, row=1, sticky=(N, S))

soundlabel = ttk.Frame(soundboard, relief=RAISED, borderwidth=2)
soundlabel.grid(column=1, row=0, sticky=(N, W, E, S))

# Controls
def Pause():
    mixer.pause()
    mixer.music.pause()
def Resume():
    mixer.unpause()
    mixer.music.unpause()

def Stop():
    Resume()
    mixer.fadeout(250)
    mixer.music.fadeout(250)

# Clear Console
def clearconsole():
    os.system('cls' if os.name=='nt' else 'clear')

def PrintErr(Where,Err):
    print("\n=====================================")
    print("Error During "+Where)
    print(Err)
    print("=====================================")

# Load Settings
InitializeSettings, Settings = SD.InitializeSettings, SD.Settings

def ShowSettings():
    print("\n[Current Settings]")
    for i in Settings:
        print(f"[{i}] ---> [{Settings[i]}]")

def UpdateSettings(Variable,Value):
    print(f"\n------------\nUpdating {Variable} to {Value}")
    Settings[Variable] = Value
    with open("Settings.json","w") as UpdateSettings:
        UpdateSettings.write(json.dumps(Settings))
    InitializeSettings() # Reload Settings
    ShowSettings()
    print("\nSettings Updated!\n------------")

def live_update():
    try:
        SongPos.set(f"{mixer.music.get_pos()/1000}s")
        LoopState.set(SD.LoopTextState)
        SpammingState.set(SD.SpammingTextState)
        root.title(f"PySoundBoard TkInter - File : {SD.Title}") if SD.LoopState == 0 else root.title(f"PySoundBoard TkInter - File : '{SD.Title}' [Loop-Enabled]")
        root.after(100, live_update)
    except Exception as Err:
        PrintErr("live_update()",Err)

def ChangeAudioDevice():
    global index
    Device = AudioDevice.get()
    try:
        UpdateSettings("AudioDevice",Device)
        mixer.quit()
        InitializeAudioSystem()
        splash()
        print(f"\n{'*'*10}\n{'Default Device' if AudioDevice.get() == 'None' else AudioDevice.get()} Found!\nSuccessfully Bound to Device!\n{'*'*10}")
        index = 0
    except Exception as Err:
        PrintErr("ChangeAudioDevice()",Err)
        print(AudioDevice.get())
        AudioDevice.set(Settings["AudioDevice"])
        ChangeAudioDevice()

def SetVol():
    try:
        Volume = float(Vol.get())/100
        if Volume >= 1:
            mixer.music.set_volume(Volume)
            Vol.set(mixer.music.get_volume()*100)
            UpdateSettings("Volume",Vol.get())
        else:
            mixer.music.set_volume(Volume)
            Vol.set(mixer.music.get_volume()*100)
            UpdateSettings("Volume",Vol.get())
    except Exception as Err:
        PrintErr("SetVol()",Err)
        print(f"\n'{Vol.get()}' is not a Valid Number between 0-100!")
        Vol.set(mixer.music.get_volume()*100)

tries, index = 0, 0
def InitializeAudioSystem():
    global tries, index
    if tries < 5:
        try:
            # perhaps make the frequency + buffer configurable in the future.
            # frequency=48000
            if Settings['AudioDevice'] is None:
                print('\nYou Do not have VB-Audio VoiceMeeter or VB-Audio Virtual Cable;\nwhich this program recognises!!\nUsing [System Default Output] !\n\nIf you do have an Output Device you wish to use, specify\nit in the [AudioDevice Input-Box] or in [Settings.json]\nIf you now have VoiceMeeter or VB-Cable Installed, simply press the "Set Device" Button to set it to them.')
            mixer.pre_init(devicename=Settings["AudioDevice"])
            mixer.init()
            mixer.music.set_volume(float(Settings['Volume'])/100)
            try:
                SD.SoundButton(r"..\startup.wav").Play() #try to look for a way to make this not be bound to only .wav files for startup sound!
            except Exception as ERR:
                PrintErr(f"InitializeAudioSystem()",ERR)
        except Exception as Err:
            time.sleep(1)
            tries += 1
            print(Settings)
            PrintErr("InitializeAudioSystem()",f"{Settings['AudioDevice']} - {Err}")
            print("Attempting Fixes...")
            
            if str(Err).lower() == 'no such device.' and index < len(DefaultValSettings):
                print(f"{index, str(Err).lower()} Setting AudioDevice to [{DefaultValSettings[index]}]")
                UpdateSettings("AudioDevice",DefaultValSettings[index])
                index += 1

            AudioDevice.set(Settings["AudioDevice"])
            InitializeAudioSystem()
            # clearconsole()
    else:
        PrintErr("InitializeAudioSystem()","\nMaximum retries Reached.\nPlease Check Settings.json\nThis can only be triggered in a manual way, so consult the 'Issues' tab on github if needed.")
        time.sleep(10)
        exit()

# Check and open then load settings
InitializeSettings()
AudioDevice.set(Settings["AudioDevice"])
Vol.set(Settings["Volume"])

# Show Current Settings
ShowSettings()

# Perform Initialization
InitializeAudioSystem()


# Show First-Time Execution then turn off pop up
if int(Settings["Splash"]) == "1":
    os.system('python Splash.py')
    UpdateSettings("Splash","0")

# initialize GUI placement and shorten
btn, lb = ttk.Button, ttk.Label

# Author and Titles
lb(headercontent, text="Soundboard written in Python! - By: Junkynioy#2408").grid(column=3, row=0,sticky=N)

# Change Audio Device
lb(headercontent, text="  AudioDevice", width=14).grid(column=2, row=1,sticky=(N,S))
SetAudDev_entry = ttk.Entry(headercontent, width=75, textvariable=AudioDevice)
SetAudDev_entry.grid(column=3,row=1,sticky=(N,S,E,W))
btn(headercontent,text="Set Device",command=ChangeAudioDevice).grid(column=4,row=1,sticky=(N,S,E,W))

# Labels and Info
lb(controllabel, text="Controls").grid(column=1, row=0,sticky=(N,S))
lb(soundlabel, text="Sound Board").grid(column=1, row=0,sticky=(N,S))

# Audio Controls
btn(controlcontent,text="Stop Playback",command=Stop).grid(column=1,row=1,sticky=(N,S,E,W))
btn(controlcontent,text="Pause Playback",command=Pause).grid(column=2,row=1,sticky=(N,S,E,W))
btn(controlcontent,text="Resume Playback",command=Resume).grid(column=3,row=1,sticky=(N,S,E,W))
SetVol_entry = ttk.Entry(controlcontent, width=7, textvariable=Vol)
SetVol_entry.grid(column=4,row=1,sticky=(W, E))
btn(controlcontent,text="< SetVolume",command=SetVol).grid(column=5,row=1,sticky=(N,S,E,W))

lb(controlcontent, textvariable=SongPos, width=10).grid(column=6, row=1,sticky=(N,S))
btn(controlcontent,text="Toggle Loop",command=SD.ToggleLoop).grid(column=7,row=1,sticky=(N,S,E,W))
lb(controlcontent, textvariable=LoopState, width=15).grid(column=8, row=1,sticky=(N, S))

btn(controlcontent,text="Multi Mode",command=SD.ToggleSpamming).grid(column=9,row=1,sticky=(N,S,E,W))
lb(controlcontent, textvariable=SpammingState, width=15).grid(column=10, row=1,sticky=(N, S))

#
# IM SO GLAD THIS WORKED!
# EVERYTHINNG IS AUTOMATED!
# POGGERS
#
ComDispName = SD.ComDispName
# len(ComDispName)/12  # 'Counter' for the amount of sounds # 'RowCounter' that gets reset every 'MaxRow'  # 'MaxRows' Until adding a new Column
try:
    if int(Settings['MaxRows']) < 0:
        PrintErr('RenderSoundBtn() Variable Init','MaxRows is <0: Set MaxRows to 0+')
    else:
        Counter, RowCounter, MaxRow = 0, 0, int(Settings['MaxRows'])
except Exception as ERR:
    PrintErr('Setting MaxRows ---> Maxrows :',f'MaxRows is Either:\n1: Does not exist! --> Delete Settings.json\n2: Value is NaN!\n\n--> : {ERR}')
def RenderSoundBtn():
    global RowCounter, MaxRow, ComDispName
    COL = 1
    try:
         for i in ComDispName:
            # text= DISPLAY NAME
            # command= CALL FUNCTION
             btn(soundbuttons, text=i[0], width=18, command=i[1]).grid(column=COL, row=RowCounter+1, sticky=(N,S,E,W))
             RowCounter += 1
             # Counter += 1
             if RowCounter >= MaxRow:
                 RowCounter = 0
                 COL += 1
         if len(ComDispName) == 0:
            print('\n\nJust drag and drop your audio files in .\\SoundFiles folder and run the Program again!')
    except Exception as Err:
        PrintErr("RenderSoundBtn()",Err)

RenderSoundBtn()

# Show GUI and Enable live_update
root.resizable(width=False, height=False)
live_update()
root.mainloop()
mixer.quit()
