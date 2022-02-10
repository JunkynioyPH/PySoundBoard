from tkinter import *
from tkinter import ttk
from pathlib import Path

import pygame
import time
import AudioDef
import json
import os

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
    print("If you have stopped audio, and it's still incrementing the 'Song Position' above 'Toggle Loop'\nJust ignore it, it does not affect anything.")

def Stop():
    pygame.mixer.music.fadeout(250)

# Clear Console
def clearconsole():
    os.system('cls' if os.name=='nt' else 'clear')

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

CheckPath2Settings()

# Show Current Settings
print("\nSettings")
print(Settings)

# initialize Values
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

# Since I cant use TTK's Progress Bar and find a working all-rounder AudioVisualizer
# I made my own Visualiser that shows that something is happening along with the
# song Position counter
#
# Its only purpose is to fill out that space that is existent at the left of the window
TextContent1 = ""
TextContent2 = ""

def AnimatedBar():
    global TextContent1, TextContent2
    SongPosition = float(pygame.mixer.music.get_pos()/1000)
    if SongPosition > 0:
        #print('pos > 0')
        TextContent1 += "|"
        AnimatedBarText1.set(TextContent1)
        AnimatedBarText2.set(TextContent2)
        if len(TextContent1) > 13:
            TextContent1 = ""
            TextContent2 += "|"
            if len(TextContent2) > 14:
                TextContent2 = ""
                # i could prolly add somethinng here, i just dont know
    else:
        #print('pos < 0')
        TextContent1 = ""
        TextContent2 = ""
        AnimatedBarText1.set(TextContent1)
        AnimatedBarText2.set(TextContent2)

def live_update():
    try:
        SongPos.set(str(pygame.mixer.music.get_pos()/1000)+"s")
        LoopState.set(AudioDef.LoopTextState)
        root.title("SoundBoard GUI - File : '"+AudioDef.AudioPath+"' is loaded.")
        root.after(250, AnimatedBar)
        root.after(100, live_update)
    except Exception as Err:
        print(Err)

def ChangeAudioDevice():
    Device = AudioDevice.get()
    try:
        pygame.mixer.quit()
        pygame.mixer.pre_init(devicename=Device)
        pygame.mixer.init()
        pygame.mixer.music.set_volume(float(Settings["Volume"])/100)
        UpdateSettings("AudioDevice",Device)
        print("\n"+AudioDevice.get()+" Found!\nSuccessfully Bound to Device!")
        AudioDef.Play("start.wav")
    except Exception as err:
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
            AudioDef.Play("start.wav")
        except Exception as Err:
            tries += 1
            print("=====================================")
            print("Error During PygameMixerInit : ")
            print(Err)
            print("=====================================")
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
        time.sleep(5)
        exit()


# Perform Initialization
InitializeAudioSystem()

# initialize GUI placement and shorten
btn = ttk.Button
lb = ttk.Label
R = 1 # To adjust Y-POS of all buttons and selected labels

# Change the Font of the program
ttk.Style().configure(".",font=('UD Digi Kyokasho N-B', 10))

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
btn(controls,text="Toggle Loop",command=AudioDef.ToggleLoop).grid(column=1,row=R+6,sticky=(N,S,E,W))
lb(controls, text="Next played has").grid(column=1, row=R+7,sticky=S)
lb(controls, textvariable=LoopState).grid(column=1, row=R+8,sticky=N)
lb(controls, textvariable=AnimatedBarText1).grid(column=1, row=R+9,sticky=N)

# Dumb Bars below the Audio Controls
lb(controls, text="]").grid(column=1, row=R+9,sticky=E)
lb(controls, text="[").grid(column=1, row=R+9,sticky=W)
lb(controls, textvariable=AnimatedBarText2).grid(column=1, row=R+10,sticky=N)
lb(controls, text="]").grid(column=1, row=R+10,sticky=E)
lb(controls, text="[").grid(column=1, row=R+10,sticky=W)

# Audio Files (Col 1)
btn(soundbuttons, text="SmashBroDrillRemix",command=AudioDef.SmashBroDrillRemix).grid(column=1,row=R,sticky=(N,S,E,W))
btn(soundbuttons, text="UltraInstinct",command=AudioDef.UltraInstinct).grid(column=1,row=R+1,sticky=(N,S,E,W))
btn(soundbuttons, text="DSoulsBossMusic",command=AudioDef.DSoulsBossMusic).grid(column=1,row=R+2,sticky=(N,S,E,W))
btn(soundbuttons, text="DSoulsDeath",command=AudioDef.DSoulsDeath).grid(column=1,row=R+3,sticky=(N,S,E,W))
btn(soundbuttons, text="ArabicRingtone",command=AudioDef.ArabicRingtone).grid(column=1,row=R+4,sticky=(N,S,E,W))
btn(soundbuttons, text="SamsungStartUp",command=AudioDef.SamsungStartUp).grid(column=1,row=R+5,sticky=(N,S,E,W))
btn(soundbuttons, text="VineBoom",command=AudioDef.VineBoom).grid(column=1,row=R+6,sticky=(N,S,E,W))
btn(soundbuttons, text="RobloxOof",command=AudioDef.RobloxOof).grid(column=1,row=R+7,sticky=(N,S,E,W))
btn(soundbuttons, text="SteveOof",command=AudioDef.SteveOof).grid(column=1,row=R+8,sticky=(N,S,E,W))
btn(soundbuttons, text="OhHarderDaddy",command=AudioDef.OhHarderDaddy).grid(column=1,row=R+9,sticky=(N,S,E,W))

# Audio Files (Col 2)
btn(soundbuttons,  text="KahootLobby", command=AudioDef.KahootLobby).grid(column=2, row=R,sticky=(N,S,E,W))
btn(soundbuttons,  text="ToBeContinued", command=AudioDef.ToBeContinued).grid(column=2, row=R+1,sticky=(N,S,E,W))
btn(soundbuttons,  text="SusImposterRole", command=AudioDef.SusImposterRole).grid(column=2, row=R+2,sticky=(N,S,E,W))
btn(soundbuttons,  text="SusBodyReported", command=AudioDef.SusBodyReported).grid(column=2, row=R+3,sticky=(N,S,E,W))
btn(soundbuttons,  text="EmotionalDamage",command=AudioDef.EmotionalDamage).grid(column=2,row=R+4,sticky=(N,S,E,W))
btn(soundbuttons,  text="ISendU2Jesus",command=AudioDef.ISendU2Jesus).grid(column=2,row=R+5,sticky=(N,S,E,W))
btn(soundbuttons,  text="YouWhat", command=AudioDef.YouWhat).grid(column=2, row=R+6,sticky=(N,S,E,W))
btn(soundbuttons,  text="WHATTHEFUCK", command=AudioDef.WHATTHEFUCK).grid(column=2, row=R+7,sticky=(N,S,E,W))
btn(soundbuttons,  text="WHAT", command=AudioDef.WHAT).grid(column=2, row=R+8,sticky=(N,S,E,W))
btn(soundbuttons,  text="Shawty", command=AudioDef.Shawty).grid(column=2, row=R+9,sticky=(N,S,E,W))

# Audio Files (Col 3)
btn(soundbuttons,  text="ThunderStorm", command=AudioDef.ThunderStorm).grid(column=3, row=R,sticky=(N,S,E,W))
btn(soundbuttons,  text="BFGDivision", command=AudioDef.BFGDivision).grid(column=3, row=R+1,sticky=(N,S,E,W))
btn(soundbuttons,  text="SmileDogMeme", command=AudioDef.SmileDogMeme).grid(column=3, row=R+2,sticky=(N,S,E,W))
btn(soundbuttons,  text="Helicopter*2", command=AudioDef.Helicopterx2).grid(column=3, row=R+3,sticky=(N,S,E,W))
btn(soundbuttons,  text="WinXPShutDown", command=AudioDef.WinXPShutDown).grid(column=3, row=R+4,sticky=(N,S,E,W))
btn(soundbuttons,  text="WinXPStartup", command=AudioDef.WinXPStartup).grid(column=3, row=R+5,sticky=(N,S,E,W))
btn(soundbuttons,  text="WinXPCritStop", command=AudioDef.WinXPCritStop).grid(column=3, row=R+6,sticky=(N,S,E,W))
btn(soundbuttons,  text="WinXPError", command=AudioDef.WinXPError).grid(column=3, row=R+7,sticky=(N,S,E,W))
btn(soundbuttons,  text="SadHarmonica(!!!)", command=AudioDef.SadHarmonicaEar).grid(column=3, row=R+8,sticky=(N,S,E,W))

# AudioFiles (Col 4)
btn(soundbuttons,  text="PHub", command=AudioDef.PHub).grid(column=4, row=R,sticky=(N,S,E,W))
btn(soundbuttons,  text="GTAWasted", command=AudioDef.GTAWasted).grid(column=4, row=R+1,sticky=(N,S,E,W))
btn(soundbuttons,  text="GiornoThemePiano", command=AudioDef.GiornoThemePiano).grid(column=4, row=R+2,sticky=(N,S,E,W))
btn(soundbuttons,  text="SickoModeWaaah", command=AudioDef.SickoModeWaaah).grid(column=4, row=R+3,sticky=(N,S,E,W))
btn(soundbuttons,  text="DreamTranceMusic", command=AudioDef.DreamTranceMusic).grid(column=4, row=R+4,sticky=(N,S,E,W))
btn(soundbuttons,  text="IndianMusicMeme", command=AudioDef.IndianMusicMeme).grid(column=4, row=R+5,sticky=(N,S,E,W))
btn(soundbuttons,  text="DJAirhorn", command=AudioDef.DJAirhorn).grid(column=4, row=R+6,sticky=(N,S,E,W))
btn(soundbuttons,  text="WhatHow_Meme", command=AudioDef.WhatHow_Meme).grid(column=4, row=R+7,sticky=(N,S,E,W))
btn(soundbuttons,  text="SadHarmonica", command=AudioDef.SadHarmonica).grid(column=4, row=R+8,sticky=(N,S,E,W))

# AudioFiles (Col 5)
btn(soundbuttons,  text="Bruh", command=AudioDef.Bruh).grid(column=5, row=R,sticky=(N,S,E,W))
btn(soundbuttons,  text="JebNooo", command=AudioDef.JebNooo).grid(column=5, row=R+1,sticky=(N,S,E,W))
btn(soundbuttons,  text="ZoneAnkha", command=AudioDef.ZoneAnkha).grid(column=5, row=R+2,sticky=(N,S,E,W))
btn(soundbuttons,  text="GangstaParadise", command=AudioDef.GangstaParadise).grid(column=5, row=R+3,sticky=(N,S,E,W))
btn(soundbuttons,  text="HeartFlatline", command=AudioDef.HeartFlatline).grid(column=5, row=R+4,sticky=(N,S,E,W))
btn(soundbuttons,  text="ChingChengHanji", command=AudioDef.ChingChengHanji).grid(column=5, row=R+5,sticky=(N,S,E,W))
btn(soundbuttons,  text="SigmaMindset", command=AudioDef.SigmaMindset).grid(column=5, row=R+6,sticky=(N,S,E,W))
btn(soundbuttons,  text="MissTheRage", command=AudioDef.MissTheRage).grid(column=5, row=R+7,sticky=(N,S,E,W))
btn(soundbuttons,  text="USSRAnthem", command=AudioDef.USSRAnthem).grid(column=5, row=R+8,sticky=(N,S,E,W))

# Show GUI and Enable live_update
root.resizable(width=False, height=False)
live_update()
root.mainloop()
pygame.quit()
