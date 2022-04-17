from tkinter import *
from tkinter import ttk
from pathlib import Path
import pygame, time, json, os
import AudioDef as AD
import SoundBtnDef as SD

# Console splash
os.system('cls' if os.name=='nt' else 'clear')
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
os.system('title PySoundBoard Backend' if os.name=='nt' else 'echo -ne "\033]0;PySoundBoard Backend\007"')
root = Tk()

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
    print("\n=====================================")
    print("Error During "+Where)
    print(Err)
    print("=====================================")

# Load Settings
def InitializeSettings():
    global Settings
    if Path("Settings.json").exists() == True:
        try:
            with open('Settings.json','r') as SettingsValue:
                Settings = json.loads(SettingsValue.read())
        except Exception as Err:
            print("\nError Occured:\n"+str(Err)+"\n")
            os.remove("Settings.json")
            print("settings.json is being reset")
            InitializeSettings()
            print("settings.json reset complete")
    else:
        x = {"AudioDevice":"CABLE Input (VB-Audio Virtual Cable)","Volume":"10","Splash":1}
        DefSettingsDump = open("Settings.json","a")
        print("settings.json [Created]")
        DefSettingsDump.write(json.dumps(x))
        print("settings.json [Accessed]")
        DefSettingsDump.close()
        print("settings.json [Closed]")
        InitializeSettings()
        print("Rerun InitializeSettings")

# Display Settings
def ShowSettings():
    print("\n[Current Settings]")
    for i in Settings:
        print("["+i+"] ---> ["+str(Settings[i])+"]")

# Update Settings
def UpdateSettings(Variable,Value):
    print("\n------------\nUpdating "+Variable+" to "+Value)
    Settings[Variable] = Value
    UpdateSettings = open("Settings.json","w")
    UpdateSettings.write(json.dumps(Settings))
    UpdateSettings.close()
    ShowSettings()
    print("\nSettings Updated!\n------------")

# Check and open then load settings
InitializeSettings()

# Show Current Settings
ShowSettings()

# Initialize Values
DefaultValSettings = ["CABLE Input (VB-Audio Virtual Cable)",10]

# Essential Values
AudioDevice, Vol, SongPos = StringVar(), StringVar(), StringVar()
AudioDevice.set(Settings["AudioDevice"])
Vol.set(Settings["Volume"])
SongPos.set('0')

# Visuals Values
LoopState = StringVar()

# for waiting for a specific key to be pressed
# temporarily non-functional, will work on it on the near future
def ScanForKeystroke():
    print('text')

def live_update():
    try:
        SongPos.set(str(pygame.mixer.music.get_pos()/1000)+"s")
        LoopState.set(AD.LoopTextState)
        root.title("SoundBoard GUI - File : '"+AD.AudioPath+"' is loaded.")
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
        print("\n*************\n"+AudioDevice.get()+" Found!\nSuccessfully Bound to Device!\n*************")
        UpdateSettings("AudioDevice",Device)
        AD.Play("start.wav")
    except Exception as Err:
        PrintErr("ChangeAudioDevice()",Err)
        print(AudioDevice.get())
        AudioDevice.set(Settings["AudioDevice"])
        ChangeAudioDevice()

def SetVol():
    try:
        Volume = float(Vol.get())/100
        if Volume >= 1:
            pygame.mixer.music.set_volume(Volume)
            Vol.set(pygame.mixer.music.get_volume()*100)
            UpdateSettings("Volume",Vol.get())
        else:
            pygame.mixer.music.set_volume(Volume)
            Vol.set(pygame.mixer.music.get_volume()*100)
            UpdateSettings("Volume",Vol.get())
    except Exception as Err:
        PrintErr("SetVol()",Err)
        print("\n'"+str(Vol.get())+"' is not a Valid Number between 0-100!")
        Vol.set(pygame.mixer.music.get_volume()*100)

# Show First-Time Execution then turn off pop up
if int(Settings["Splash"]) == "1":
    os.system('python Splash.py')
    UpdateSettings("Splash","0")

# Start audio system
tries = 0
def InitializeAudioSystem():
    global tries
    if tries < 10:
        try:
            pygame.mixer.pre_init(devicename=Settings["AudioDevice"])
            pygame.mixer.init()
            pygame.mixer.music.set_volume(float(Vol.get())/100)
            AD.Play("start.wav")
        except Exception as Err:
            time.sleep(1)
            tries += 1
            PrintErr("InitializeAudioSystem()",Err)
            print(Settings)
            print("AudioDevice & Volume Settings is reset with the hopes of fixing the issue.\nSorry for the inconvenience.\n\nIf this did not fix the issue, please create a 'New Issue' on the github page.\nhttps://github.com/JunkynioyPH/PySoundBoard/issues \n")
            UpdateSettings("AudioDevice",DefaultValSettings[0])
            UpdateSettings("Volume",DefaultValSettings[1])
            AudioDevice.set(Settings["AudioDevice"])
            InitializeAudioSystem()
            SetVol()
    else:
        PrintErr("InitializeAudioSystem()","\nMaximum retries Reached. (40 Retries)\nThis could mean you do not have VoiceMeeter Installed.\nChange the AudioDevice in Settings.json")
        time.sleep(10)
        exit()


# Perform Initialization
InitializeAudioSystem()

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
btn(controlcontent,text="Toggle Loop",command=AD.ToggleLoop).grid(column=7,row=1,sticky=(N,S,E,W))
lb(controlcontent, textvariable=LoopState, width=15).grid(column=8, row=1,sticky=(N, S))

#
# IM SO GLAD THIS WORKED!
# EVERYTHINNG IS AUTOMATED!
# POGGERS
#
ComDispName = SD.ComDispName
Counter, RowCounter, MaxRow = 0, 0, 13     # 'Counter' for the amount of sounds # 'RowCounter' that gets reset every 'MaxRow'  # 'MaxRows' Until adding a new Column
def RenderSoundBtn():
    global Counter, RowCounter, MaxRow, ComDispName
    COL = 1
    try:
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
