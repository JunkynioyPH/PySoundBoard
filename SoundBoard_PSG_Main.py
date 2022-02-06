from pathlib import Path
import PySimpleGUI as sg
import pygame
import time
import AudioDef as ad
import SoundDef as sd
import json
import os

# Set Theme
sg.theme('Dark Grey 13')

# The Brains
os.system("title SoundBoard Backend")

# Load Settings
DefaultValSettings = ["CABLE Input (VB-Audio Virtual Cable)",10]

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

# First-Time Startup Message
# Make this only one time
if int(Settings["Splash"]) == 1:
    sg.popup_ok('Note that this program assumes you have \nVoiceMeeter & VB-Audio Virtual Cable\nalready setup.\n\nUnless you know what you are doing\nYou will have to manually set\nthe audio device in settings.json.\nElse it will just not work.')
    UpdateSettings("Splash",0)

# Shorten
def lb(text):
    return sg.Text(text)

def btn(text):
    return sg.Button(text,size=(15,1),pad=(0,0))
ip = sg.Input

# Cant think of a way to make it so 1 list = multiple rows and columns
def SoundButtons(Sound):
    return [btn(SoundName) for SoundName in Sound]

# GUI Layout
layout = [
    # Top Banner
    [
        [lb('Soundboard written in Python! - By: Junkynioy#2408')],
        [lb("AudioDevice "), ip(Settings["AudioDevice"],key='-AUDIODEVICE-'), btn('Set Device'), ip(Settings['Volume'],size=(8,1),key='-AUDIOVOLUME-'), btn('Set Volume')]
    ],
    # Main Frame
    [
        # Control Buttons
        [
            lb('Controls'), btn('Stop Playback'), btn('Pause Playback'), btn('Resume Playback'), lb('DURATION'), btn('Toggle Loop'), lb('Next played has'), lb('T/F LOOPING')
        ],
        # SoundBoard
        [
            SoundButtons(sd.Sounds1),
            SoundButtons(sd.Sounds2),
            SoundButtons(sd.Sounds3),
            SoundButtons(sd.Sounds4),
            SoundButtons(sd.Sounds5),
            SoundButtons(sd.Sounds6),
            SoundButtons(sd.Sounds7)
        ]
    ]
]
window = sg.Window('SoundBoard PySimpleGUI', layout)
window.Finalize()

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

print("\nSettings")
print(Settings)

def ChangeAudioDevice():
    Device = values['-AUDIODEVICE-']
    try:
        pygame.mixer.quit()
        pygame.mixer.pre_init(devicename=Device)
        pygame.mixer.init()
        pygame.mixer.music.set_volume(float(Settings["Volume"])/100)
        UpdateSettings("AudioDevice",Device)
        print("\n"+str(values['-AUDIODEVICE-'])+" Found!\nSuccessfully Bound to Device!")
        ad.Play("start.wav")
    except Exception as err:
        print("\nThere's "+str(err)+"\n"+str(values['-AUDIODEVICE-']))
        values['-AUDIODEVICE-'] = Settings['AudioDevice']
        window['-AUDIODEVICE-'].update(Settings['AudioDevice'])
        ChangeAudioDevice()

def SetVol():
    try:
        Volume = float(values['-AUDIOVOLUME-'])/100
        if Volume >= 1:
            pygame.mixer.music.set_volume(Volume)
            print("\nVolume is now set to '100%'!")
            window['-AUDIOVOLUME-'].update(pygame.mixer.music.get_volume()*100)
            UpdateSettings("Volume",values['-AUDIOVOLUME-'])
        else:
            pygame.mixer.music.set_volume(Volume)
            print("\nVolume changed to '"+values['-AUDIOVOLUME-']+"%'!")
            window['-AUDIOVOLUME-'].update(pygame.mixer.music.get_volume()*100)
            UpdateSettings("Volume",values['-AUDIOVOLUME-'])
    except Exception as err:
        print("\n'"+str(values['-AUDIOVOLUME-'])+"' is not a Valid Number between 0-100!")
        window['-AUDIOVOLUME-'].update(pygame.mixer.music.get_volume()*100)

tries = 0
def InitializeAudioSystem():
    global tries
    if tries < 40:
        try:
            pygame.mixer.pre_init(devicename=Settings["AudioDevice"])
            pygame.mixer.init()
            pygame.mixer.music.set_volume(float(Settings['Volume'])/100)
            ad.Play("start.wav")
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
            #values['-AUDIODEVICE-'].update(Settings["AudioDevice"])
            InitializeAudioSystem()
            #SetVol()
    else:
        os.system('color 0c')
        print("\n\nMaximum speed-retries Reached. (40 Retries)")
        time.sleep(5)
        exit()

# Perform Initialization
InitializeAudioSystem()

# Main Loop
while True:
    event, values = window.read()
    match event:
        case sg.WINDOW_CLOSED:
            pygame.quit()
            break
        case 'Set Device':
            ChangeAudioDevice()
        case 'Set Volume':
            SetVol()
        case 'Stop Playback':
            Stop()
        case 'Pause Playback':
            Pause()
        case 'Resume Playback':
            Resume()
        case 'Toggle Loop':
            ad.ToggleLoop()
        case 'ZoneAnkha':
            ad.ZoneAnkha()
        case _:
            print("Something Went Wrong... oops.")
