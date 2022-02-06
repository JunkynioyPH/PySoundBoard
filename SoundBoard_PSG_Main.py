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

Sounds = [
"SmashBroDrillRemix",
"UltraInstinct",
"DSoulsBossMusic",
"DSoulsDeath",
"ArabicRingtone",
"SamsungStartUp",
"VineBoom",
"RobloxOof",
"SteveOof",
"OhHarderDaddy",
"KahootLobby",
"ToBeContinued",
"SusImposterRole",
"SusBodyReported",
"EmotionalDamage",
"ISendU2Jesus",
"YouWhat",
"WHATTHEFUCK",
"WHAT",
"ThunderStorm",
"BFGDivision",
"SmileDogMeme",
"Helicopterx2",
"WinXPShutDown",
"WinXPStartup",
"WinXPCritStop",
"WinXPError",
"SadHarmonicaEar",
"PHub",
"GTAWasted",
"GiornoThemePiano",
"SickoModeWaaah",
"DreamTranceMusic",
"IndianMusicMeme",
"DJAirhorn",
"WhatHow_Meme",
"SadHarmonica",
"Bruh",
"JebNooo",
"ZoneAnkha",
"GangstaParadise",
"HeartFlatline",
"ChingChengHanji",
"SigmaMindset",
"MissTheRage",
"USSRAnthem"
]

# shorten
lb  = sg.Text
btn = sg.Button

layout = [
    # Top Banner
    [
        [lb('Soundboard written in Python! - By: Junkynioy#2408')],
        [lb("AudioDevice "), sg.Input('CABLE Input (VB-Audio Virtual Cable)',key='-AUDIODEVICE-'), btn('Set Device')]
    ],
    # Main Frame
    [
        # Control Buttons
        [
            lb('Controls'), btn('Stop Playback'), btn('Pause Playback'), btn('Resume Playback'), lb('DURATION'), btn('Toggle Loop'), lb('Next played has'), lb('T/F LOOPING')
        ],
        # SoundBoard
        [

        ]
    ]
]
window = sg.Window('SoundBoard PySimpleGUI', layout)

# This will create the Window and read window if already exists, make sure to add this in While Main Loop
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
