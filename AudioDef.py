import pygame
import os
import time

LoopState = 0
LoopTextState = "No Loop"

def ToggleLoop():
    global LoopState, LoopTextState
    if LoopState == 0:
        LoopTextState = "Looping"
        LoopState = -1
    else:
        LoopTextState = "No Loop"
        LoopState = 0

def Play(AudioFile):
    global LoopState, LoopTextState, AudioPath
    AudioPath = AudioFile
    pygame.mixer.music.unload()
    pygame.mixer.music.load(AudioFile)
    pygame.mixer.music.play(loops=LoopState)
    pygame.init()

def SmashBroDrillRemix():
    Play(".\SoundFiles\\smashbrodrillremix.mp3")

def VineBoom():
    Play(".\SoundFiles\\vineboom.mp3")

def DreamTranceMusic():
    Play(".\SoundFiles\\dreamtrancemusic.mp3")

def DSoulsDeath():
    Play(".\SoundFiles\\dsoulsdeath.mp3")

def RobloxOof():
    Play(".\SoundFiles\\robloxoof.mp3")

def SteveOof():
    Play(".\SoundFiles\\steveoof.mp3")

def SamsungStartUp():
    Play(".\SoundFiles\\samsungstartup.mp3")

def UltraInstinct():
    Play(".\SoundFiles\\ultrainstinct.mp3")

def ZoneAnkha():
    Play(".\SoundFiles\\zoneankha.mp3")

def GangstaParadise():
    Play(".\SoundFiles\\gangstaparadise.mp3")

def GiornoThemePiano():
    Play(".\Soundfiles\\giornothemepiano.mp3")

def SickoModeWaaah():
    Play(".\SoundFiles\\sickomodewaaah.mp3")

def DSoulsBossMusic():
    Play(".\SoundFiles\\dsoulsbossmusic.mp3")

def ArabicRingtone():
    Play(".\SoundFiles\\arabicringtone.mp3")

def IndianMusicMeme():
    Play(".\SoundFiles\\panjabimc.mp3")

def SusBodyReported():
    Play(".\SoundFiles\\susbodyreported.mp3")

def EmotionalDamage():
    Play(".\SoundFiles\\emotionaldamage.mp3")

def JebNooo():
    Play(".\SoundFiles\\jebnooo.mp3")

def Bruh():
    Play('.\SoundFiles\\bruh.mp3')

def ChingChengHanji():
    Play('.\SoundFiles\\chingchenghanji.mp3')

def YouWhat():
    Play('.\SoundFiles\\youwhat.mp3')

def SusImposterRole():
    Play(".\SoundFiles\\susimposterrole.mp3")

def SadHarmonicaEar():
    Play(".\SoundFiles\\sadharmonicaEar.mp3")

def SadHarmonica():
    Play(".\SoundFiles\\sadharmonica.mp3")

def DJAirhorn():
    Play(".\SoundFiles\\djairhorn.mp3")

def ISendU2Jesus():
    Play(".\SoundFiles\\isendu2jesus.mp3")

def SmileDogMeme():
    Play(".\SoundFiles\\smiledogmeme.mp3")

def Helicopterx2():
    Play(".\SoundFiles\\helicopterx2.mp3")

def WHATTHEFUCK():
    Play(".\SoundFiles\\wtf.ogg")

def WHAT():
    Play(".\SoundFiles\\wat.ogg")

def ToBeContinued():
    Play(".\SoundFiles\\tbc.mp3")

def PHub():
    Play(".\SoundFiles\\phub.mp3")

def ThunderStorm():
    Play(".\SoundFiles\\thunderstorm.mp3")

def KahootLobby():
    Play(".\SoundFiles\\kahootlobby.mp3")

def HeartFlatline():
    Play(".\SoundFiles\\heartflatline.mp3")

def WhatHow_Meme():
    Play(".\SoundFiles\\whathowmeme.mp3")

def GTAWasted():
    Play(".\SoundFiles\\gtawasted.mp3")

def BFGDivision():
    Play(".\SoundFiles\\bfgdivision.mp3")

def WinXPShutDown():
    Play(".\SoundFiles\\winxpshutdown.wav")

def WinXPStartup():
    Play(".\SoundFiles\\winxpstartup.wav")

def WinXPCritStop():
    Play(".\SoundFiles\\winxpcritstop.wav")

def WinXPError():
    Play(".\SoundFiles\\winxperror.wav")
