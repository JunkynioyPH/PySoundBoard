import pygame
import os
import time

LoopTextState, LoopState = "  No   Looping", 0

def ToggleLoop():
    global LoopState, LoopTextState
    if LoopState == 0:
        LoopTextState, LoopState = "  Yes Looping", -1
    else:
        LoopTextState, LoopState = "  No   Looping", 0

def PrintErr(Where,Err):
    print("\n=====================================")
    print("Error During "+Where)
    print(Err)
    print("=====================================")

def Play(AudioFile):
    global LoopState, LoopTextState, AudioPath
    try:
        AudioPath = AudioFile # for the window title
        pygame.mixer.music.unload()
        pygame.mixer.music.load(".\SoundFiles\\"+AudioFile)
        pygame.mixer.music.play(loops=LoopState)
    except Exception as Err:
        PrintErr('AudioDef.Play()',Err)

def SmashBroDrillRemix():
    Play("smashbrodrillremix.mp3")

def McChallengeGet():
    Play("mcchallengeget.mp3")

def VineBoom():
    Play("vineboom.mp3")

def AnimeBonk():
    Play('animebonk.mp3')

def TacoBellBoom():
    Play("tacobellboom.mp3")

def CatUP():
    Play('catup.mp3')

def CatDOWN():
    Play('catdown.mp3')

def WidePutin():
    Play('wideputin.mp3')

def McCaveNoise():
    Play('mccavenoise.mp3')

def DreamTranceMusic():
    Play("dreamtrancemusic.mp3")

def DSoulsDeath():
    Play("dsoulsdeath.mp3")

def DarudeSandstorm():
    Play("darudesandstorm.mp3")

def RobloxOof():
    Play("robloxoof.mp3")

def SteveOof():
    Play("steveoof.mp3")

def BoyWithUkeToxic():
    Play("boywithuketoxic.mp3")

def SamsungStartUp():
    Play("samsungstartup.mp3")

def SusRemix():
    Play('susremix.mp3')

def JPRickRoll():
    Play('jprickroll.mp3')

def RickRoll():
    Play('rickroll.mp3')

def JPSusRemix():
    Play('jpsusremix.mp3')

def LionSleepsTonight():
    Play('lionsleepstonight.mp3')

def UltraInstinct():
    Play("ultrainstinct.mp3")

def OsmanthusWine():
    Play('osmanthuswine.mp3')

def SpidermanBSuit():
    Play('spidermanbsuit.mp3')

def AnimeGirlAH():
    Play('animegirlah.mp3')

def YTFULying():
    Play('ytfulying.mp3')

def Yamete():
    Play('yamete.mp3')

def YameteKudasai():
    Play('yametekudasai.mp3')

def OsManThuSWinE():
    Play('ozmenthuswayn.mp3')

def ZoneAnkha():
    Play("zoneankha.mp3")

def GangstaParadise():
    Play("gangstaparadise.mp3")

def GiornoThemePiano():
    Play("giornothemepiano.mp3")

def SickoModeWaaah():
    Play("sickomodewaaah.mp3")

def DSoulsBossMusic():
    Play("dsoulsbossmusic.mp3")

def ArabicRingtone():
    Play("arabicringtone.mp3")

def Bonk():
    Play("bonk.mp3")

def ReZeroGigguk():
    Play("rezerogigguk.mp3")

def Unravel():
    Play("unravel.mp3")

def OhHarderDaddy():
    Play("ohharderdaddy.mp3")

def SusBodyReported():
    Play("susbodyreported.mp3")

def EmotionalDamage():
    Play("emotionaldamage.mp3")

def JebNooo():
    Play("jebnooo.mp3")

def Bruh():
    Play('bruh.mp3')

def Shawty():
    Play('shawty.mp3')

def SigmaMindset():
    Play('sigmamindset.mp3')

def MissTheRage():
    Play('misstherage.mp3')

def USSRAnthem():
    Play('ussranthem.mp3')

def YouWhat():
    Play('youwhat.mp3')

def SusImposterRole():
    Play("susimposterrole.mp3")

def SadHarmonicaEar():
    Play("sadharmonicaEar.mp3")

def SadHarmonica():
    Play("sadharmonica.mp3")

def DJAirhorn():
    Play("djairhorn.mp3")

def ISendU2Jesus():
    Play("isendu2jesus.mp3")

def SmileDogMeme():
    Play("smiledogmeme.mp3")

def Helicopterx2():
    Play("helicopterx2.mp3")

def WHATTHEFUCK():
    Play("wtf.ogg")

def WHAT():
    Play("wat.ogg")

def ToBeContinued():
    Play("tbc.mp3")

def PHub():
    Play("phub.mp3")

def ThunderStorm():
    Play("thunderstorm.mp3")

def KahootLobby():
    Play("kahootlobby.mp3")

def HeartFlatline():
    Play("heartflatline.mp3")

def WhatHow_Meme():
    Play("whathowmeme.mp3")

def GTAWasted():
    Play("gtawasted.mp3")

def BFGDivision():
    Play("bfgdivision.mp3")

def WinXPShutDown():
    Play("winxpshutdown.wav")

def WinXPStartup():
    Play("winxpstartup.wav")

def WinXPCritStop():
    Play("winxpcritstop.wav")

def WinXPError():
    Play("winxperror.wav")
