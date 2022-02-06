from pathlib import Path
import PySimpleGUI as sg
import pygame
import time
import AudioDef
import json
import os

# Set Theme
sg.theme('Dark Grey 13')

# First-Time Startup Message
# Make this only one time
sg.popup_ok('Note that this program assumes you have \nVoiceMeeter & VB-Audio Virtual Cable\nalready setup.\n\nUnless you know what you are doing\nYou will have to manually set\nthe audio device in settings.json.\nElse it will just not work.')

layout = [
    # Top Banner
    [
    [sg.Text('Soundboard written in Python! - By: Junkynioy#2408')],
    [sg.Text("AudioDevice "), sg.Input(key='-AUDIODEVICE-')]
    ]
]
window = sg.Window('SoundBoard PySimpleGUI', layout)

# This will create the Window and read window if already exists, make sure to add this in While Main Loop
while True:
    event, values = window.read()
    print(values)
    if event == sg.WINDOW_CLOSED:
        break
