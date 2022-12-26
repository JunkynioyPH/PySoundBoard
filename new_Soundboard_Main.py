from tkinter import *
from tkinter import ttk
from pathlib import Path
from pygame import mixer
import time, json, os
import SoundBtnDef as SD
import AudioDef as AD

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

DefaultValSettings = ["CABLE Input (VB-Audio Virtual Cable)",10]

# Essential Values
AudioDevice, Vol, SongPos = StringVar(), StringVar(), StringVar()
AudioDevice.set(Settings["AudioDevice"])
Vol.set(Settings["Volume"])
SongPos.set('0')

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
    mixer.music.pause()

def Resume():
    mixer.music.unpause()

def Stop():
    Resume()
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
        x = {"AudioDevice":"CABLE Input (VB-Audio Virtual Cable)","Volume":"10","Splash":"1"}
        DefSettingsDump = open("Settings.json","a")
        print("settings.json [Created]")
        DefSettingsDump.write(json.dumps(x))
        print("settings.json [Accessed]")
        DefSettingsDump.close()
        print("settings.json [Closed]")
        InitializeSettings()
        print("Rerun InitializeSettings")

def ShowSettings():
    print("\n[Current Settings]")
    for i in Settings:
        print("["+i+"] ---> ["+str(Settings[i])+"]")

def UpdateSettings(Variable,Value):
    print(f"\n------------\nUpdating {Variable} to {Value}")
    Settings[Variable] = Value
    UpdateSettings = open("Settings.json","w")
    UpdateSettings.write(json.dumps(Settings))
    UpdateSettings.close()
    ShowSettings()
    print("\nSettings Updated!\n------------")