from os import environ
environ["QT_FFMPEG_LOG_LEVEL"] = "fatal"
environ["QT_LOGGING_RULES"] = "*.debug=false;qt.multimedia.*=false"
import sys
from AudioSystem_PyQt6 import *
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import QApplication

APP = QApplication([])
device = [QMediaDevices.audioOutputs()[2],QMediaDevices.defaultAudioOutput()]
AudioSystem = AudioManager(device[1],
                            {'master':SoundType.MASTER_VOLUME,
                            'sfxMaster':SoundType.MASTER_VOLUME,
                            'sfx.name':SoundType.SOUND_EFFECT})


AudioSystem.addIndex(SoundType.SOUND_EFFECT,"./SoundFiles/funny sfx/Asterisk.wav")
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')

AudioSystem.status()
AudioSystem.unloadSoundEffectObj('sfx.name',0)
AudioSystem.status()
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.status()



sys.exit(APP.exec())