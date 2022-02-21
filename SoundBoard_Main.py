from tkinter import *
from tkinter import ttk
from pathlib import Path

import pygame
import time
import AudioDef as AD
import SoundBtnDef as SD
import json
import os

# Console splash
print('''
██████╗ ██╗   ██╗███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██████╗  ██████╗  █████╗ ██████╗ ██████╗
██╔══██╗╚██╗ ██╔╝██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
██████╔╝ ╚████╔╝ ███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║
██╔═══╝   ╚██╔╝  ╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║
██║        ██║   ███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
                    Written By : Junkynioy#2408 - https://github.com/JunkynioyPH
''')

# Preliminary preparations
os.system("title SoundBoard Backend")
root = Tk()
root.title("SoundBoard GUI")

# Cointainers
header = ttk.Frame(root, relief=RAISED, borderwidth=8)
header.grid(padx=5, pady=5, column=0, row=0, sticky=(N, W, E, S))

mframe = ttk.Frame(root, relief=GROOVE, borderwidth=2)
mframe.grid(padx=10, pady=10, column=0, row=1, sticky=(N, W, E, S))

controls = ttk.Frame(mframe, relief=SUNKEN, borderwidth=2)
controls.grid(padx=5, pady=5, column=0, row=0, sticky=(N, W, E, S))

soundboard = ttk.Frame(mframe, relief=SUNKEN, borderwidth=2)
soundboard.grid(padx=5, pady=5, column=1, row=0, sticky=(N, W, E, S))

soundbuttons = ttk.Frame(soundboard, relief=SUNKEN, borderwidth=2)
soundbuttons.grid(padx=5, pady=5, column=1, row=1, sticky=(N, W, E, S))

controllabel = ttk.Frame(controls, relief=RAISED, borderwidth=2)
controllabel.grid(column=1, row=0, sticky=(N, W, E, S))

soundlabel = ttk.Frame(soundboard, relief=RAISED, borderwidth=2)
soundlabel.grid(column=1, row=0, sticky=(N, W, E, S))

# Controls
def Pause():
    pygame.mixer.music.pause()

def Resume():
    pygame.mixer.music.unpause()

def Stop():
    Resume()
    pygame.mixer.music.fadeout(250)

# Clear Console
def clearconsole():
    os.system('cls' if os.name=='nt' else 'clear')

def PrintErr(Where,Err):
    print("=====================================")
    print("Error During "+Where)
    print(Err)
    print("=====================================")

# Load Settings
def CheckPath2Settings():
    global Settings
    if Path("Settings.json").exists() == True:
        try:
            with open('Settings.json','r') as SettingsValue:
                SettingsData = SettingsValue.read()
            Settings = json.loads(SettingsData)
        except Exception as Err:
            print("\nError Occured:\n"+str(Err)+"\n")
            os.remove("Settings.json")
            print("settings.json is being reset")
            CheckPath2Settings()
            print("settings.json reset complete")
    else:
        x = {"AudioDevice":"CABLE Input (VB-Audio Virtual Cable)","Volume":"10","Splash":1}
        DefSettingsDump = open("Settings.json","a")
        print("settings.json is made")
        DefSettingsDump.write(json.dumps(x))
        print("settings.json is written to")
        DefSettingsDump.close()
        print("settings.json is closed")
        CheckPath2Settings()
        print("Rerun CheckPath2Settings")

# Update Settings
def UpdateSettings(Variable,Value):
    Settings[Variable] = Value
    UpdateSettings = open("Settings.json","w")
    print("\nsettings.json is opened")
    UpdateSettings.write(json.dumps(Settings))
    print("settings.json is updated")
    UpdateSettings.close()
    print(Settings)

# Check and open then load settings
CheckPath2Settings()

# Show Current Settings
print("\nCurrent Settings")
print(Settings)

# Initialize Values
DefaultValSettings = ["CABLE Input (VB-Audio Virtual Cable)",10]

AudioDevice = StringVar()
AudioDevice.set(Settings["AudioDevice"])

Vol = StringVar()
Vol.set(Settings["Volume"])

SongPos = StringVar()
SongPos.set('0')

LoopState = StringVar()

AnimatedBarText1 = StringVar()
AnimatedBarText2 = StringVar()

#
# Since I cant use TTK's Progress Bar and find a working all-rounder AudioVisualizer
# I made my own Visualiser that shows that something is happening along with the
# song Position counter
#
# Its only purpose is to fill out that space that is existent at the left of the window
#
TextContents = ["","","",""]
def AnimatedBar():
    SongPosition = float(pygame.mixer.music.get_pos()/1000)
    if SongPosition > 0:
        #print('pos > 0')
        TextContents[0] += "|"
        AnimatedBarText1.set(TextContents[0])
        AnimatedBarText2.set(TextContents[1])
        if len(TextContents[0]) > 13:
            TextContents[0] = ""
            TextContents[1] += "|"
            if len(TextContents[1]) > 14:
                TextContents[1] = ""
                # i could prolly add somethinng here, i just dont know
    else:
        #print('pos < 0')
        for i in range(0,len(TextContents)):
            TextContents[i] = ""
        AnimatedBarText1.set(TextContents[0])
        AnimatedBarText2.set(TextContents[1])

def live_update():
    try:
        SongPos.set(str(pygame.mixer.music.get_pos()/1000)+"s")
        LoopState.set(AD.LoopTextState)
        root.title("SoundBoard GUI - File : '"+AD.AudioPath+"' is loaded.")
        root.after(250, AnimatedBar)
        root.after(100, live_update)
    except Exception as Err:
        PrintErr("live_update()",Err)

def ChangeAudioDevice():
    Device = AudioDevice.get()
    try:
        pygame.mixer.quit()
        pygame.mixer.pre_init(devicename=Device)
        pygame.mixer.init()
        pygame.mixer.music.set_volume(float(Settings["Volume"])/100)
        UpdateSettings("AudioDevice",Device)
        print("\n"+AudioDevice.get()+" Found!\nSuccessfully Bound to Device!")
        AD.Play("start.wav")
    except Exception as err:
        PrintErr("ChangeAudioDevice()",Err)
        print("\nThere's "+str(err)+"\n"+AudioDevice.get())
        AudioDevice.set(Settings["AudioDevice"])
        ChangeAudioDevice()

def SetVol():
    try:
        Volume = float(Vol.get())/100
        if Volume >= 1:
            pygame.mixer.music.set_volume(Volume)
            print("\nVolume is now set to '100%'!")
            Vol.set(pygame.mixer.music.get_volume()*100)
            UpdateSettings("Volume",Vol.get())
        else:
            pygame.mixer.music.set_volume(Volume)
            print("\nVolume changed to '"+Vol.get()+"%'!")
            Vol.set(pygame.mixer.music.get_volume()*100)
            UpdateSettings("Volume",Vol.get())
    except Exception as err:
        PrintErr("SetVol()",Err)
        print("\n'"+str(Vol.get())+"' is not a Valid Number between 0-100!")
        Vol.set(pygame.mixer.music.get_volume()*100)

# Show First-Time Execution then turn off pop up
if int(Settings["Splash"]) == 1:
    os.system('python Splash.py')
    UpdateSettings("Splash",0)

# Start audio system
tries = 0
def InitializeAudioSystem():
    global tries
    if tries < 40:
        try:
            pygame.mixer.pre_init(devicename=Settings["AudioDevice"])
            pygame.mixer.init()
            pygame.mixer.music.set_volume(float(Vol.get())/100)
            AD.Play("start.wav")
        except Exception as Err:
            tries += 1
            PrintErr("InitializeAudioSystem()",Err)
            print(Settings)
            print("AudioDevice & Volume Settings is reset with the hopes of fixing the issue.\nSorry for the inconvenience.\n\nIf this did not fix the issue, please create a 'New Issue' on the github page.\nhttps://github.com/JunkynioyPH/PySoundBoard/issues")
            UpdateSettings("AudioDevice",DefaultValSettings[0])
            UpdateSettings("Volume",DefaultValSettings[1])
            AudioDevice.set(Settings["AudioDevice"])
            InitializeAudioSystem()
            SetVol()
    else:
        os.system('color 0c')
        print("\n\nMaximum speed-retries Reached. (40 Retries)")
        print("This could mean you do not have VoiceMeeter Installed.\nChange the AudioDevice in Settings.json")
        time.sleep(10)
        exit()


# Perform Initialization
InitializeAudioSystem()

# initialize GUI placement and shorten
btn = ttk.Button
lb = ttk.Label
R = 1 # To adjust Y-POS of all buttons and selected labels

# Change the Font of the program
ttk.Style().configure(".",font=('Trebuchet MS Bold', 8))

# Author and Titles
lb(header, text="Soundboard written in Python! - By: Junkynioy#2408").grid(column=3, row=1,sticky=N)

# Change Audio Device
lb(header, text="       ").grid(column=1, row=2,sticky=E)
lb(header, text="AudioDevice").grid(column=2, row=2,sticky=E)
SetAudDev_entry = ttk.Entry(header, width=75, textvariable=AudioDevice)
SetAudDev_entry.grid(column=3,row=2,sticky=(N,S,E,W))
btn(header,text="Set Device",command=ChangeAudioDevice).grid(column=4,row=2,sticky=(N,S,E,W))

# Labels and Info
lb(controllabel, text="Controls").grid(column=1, row=0,sticky=(N,S,E,W))
lb(soundlabel, text="Sound Board").grid(column=1, row=0,sticky=(N,S,E,W))

# Audio Controls
btn(controls,text="Stop Playback",command=Stop).grid(column=1,row=R,sticky=(N,S,E,W))
btn(controls,text="Pause Playback",command=Pause).grid(column=1,row=R+1,sticky=(N,S,E,W))
btn(controls,text="Resume Playback",command=Resume).grid(column=1,row=R+2,sticky=(N,S,E,W))
SetVol_entry = ttk.Entry(controls, width=7, textvariable=Vol)
SetVol_entry.grid(column=1,row=R+3,sticky=(W, E))
btn(controls,text="^ SetVolume",command=SetVol).grid(column=1,row=R+4,sticky=(N,S,E,W))
lb(controls, textvariable=SongPos).grid(column=1, row=R+5,sticky=(N,S))
btn(controls,text="Toggle Loop",command=AD.ToggleLoop).grid(column=1,row=R+6,sticky=(N,S,E,W))
lb(controls, text="Next played has").grid(column=1, row=R+7,sticky=S)
lb(controls, textvariable=LoopState).grid(column=1, row=R+8,sticky=N)

# Dumb Bars below the Audio Controls
lb(controls, textvariable=AnimatedBarText1).grid(column=1, row=R+9,sticky=N)
lb(controls, text="]").grid(column=1, row=R+9,sticky=E)
lb(controls, text="[").grid(column=1, row=R+9,sticky=W)
lb(controls, textvariable=AnimatedBarText2).grid(column=1, row=R+10,sticky=N)
lb(controls, text="]").grid(column=1, row=R+10,sticky=E)
lb(controls, text="[").grid(column=1, row=R+10,sticky=W)

# I want to add something in these, idk what though
lb(controls, text="").grid(column=1, row=R+11,sticky=W)
lb(controls, text="").grid(column=1, row=R+12,sticky=W)
lb(controls, text="").grid(column=1, row=R+13,sticky=W)
lb(controls, text="").grid(column=1, row=R+14,sticky=W)

#
# IM SO GLAD THIS WORKED!
# EVERYTHINNG IS AUTOMATED!
# POGGERS
#
ComDispName = SD.ComDispName
Counter = 0     # Overall Counter for the amount of sounds
RowCounter = 0  # Counter that gets resert every MaxRow
MaxRow = 12     # MaxRows Until adding a new Column
def RenderSoundBtn():
    global Counter, RowCounter, MaxRow, ComDispName
    COL = 1
    try:
         if Counter <= len(ComDispName):
             for i in ComDispName:
                 btn(soundbuttons, text=i[0], width=18, command=ComDispName[Counter][1]).grid(column=COL, row=RowCounter+1, sticky=(N,S,E,W))
                 RowCounter += 1
                 Counter += 1
                 if RowCounter >= MaxRow:
                     RowCounter = 0
                     COL += 1
    except Exception as Err:
        PrintErr("RenderSoundBtn()",Err)

RenderSoundBtn()

# Show GUI and Enable live_update
root.resizable(width=False, height=False)
live_update()
root.mainloop()
pygame.quit()
