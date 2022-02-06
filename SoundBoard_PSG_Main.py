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







# First-Time Startup Message
# Make this only one time
sg.popup_ok('Note that this program assumes you have \nVoiceMeeter & VB-Audio Virtual Cable\nalready setup.\n\nUnless you know what you are doing\nYou will have to manually set\nthe audio device in settings.json.\nElse it will just not work.')

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
        [lb("AudioDevice "), ip('TEMPORARY VALUE',key='-AUDIODEVICE-'), btn('Set Device'), ip('TEMPORARY VALUE',size=(8,1),key='-AUDIOVOLUME-'), btn('Set Volume')]
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

# Main Loop
while True:
    event, values = window.read()
    print(values)
    match event:
        case sg.WINDOW_CLOSED:
            break
        case 'Set Device':
            print('set device'+str(values['-AUDIODEVICE-']))
        case _:
            print("Something Went Wrong... oops.")
