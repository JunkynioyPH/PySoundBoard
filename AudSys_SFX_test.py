from os import environ
environ["QT_FFMPEG_LOG_LEVEL"] = "fatal"
environ["QT_LOGGING_RULES"] = "*.debug=false;qt.multimedia.*=false"
import sys
from PyQt6.QtCore import Qt, QTimer
from AudioSystem_PyQt6 import *
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import QApplication
APP = QApplication([])
class updateTimerQueue(QTimer):
    def __init__(self, parent=None, ticks:int|None=None):
        super().__init__(parent)
        self.updateList:list = []
        self.timeout.connect(self.update)
        self.start(ticks) if ticks else self.start(250)
    def update(self):
        for item in self.updateList:
            item()
    def appendToQueue(self, _callable):
        rich.print('[PySoundboard] UpdateTimerQueue: ', end='')
        if not callable(_callable):
            return rich.print(f'[red]Not Callable [/red]{_callable}')
        rich.print(f'[green]Appended [/green]{_callable}')
        self.updateList.append(_callable)
    def popQueueItem(self, index:int):
        self.updateList.pop(index)
device = [QMediaDevices.audioOutputs()[2],QMediaDevices.defaultAudioOutput()]
AudioSystem = AudioManager(device[1],
                            {'master':SoundType.MASTER_VOLUME,
                            'sfxMaster':SoundType.MASTER_VOLUME,
                            'sfx.name':SoundType.SOUND_EFFECT,
                            'audio':SoundType.AUDIO_MEDIA,
                            'audio1':SoundType.AUDIO_MEDIA})

respondToMyShitty_CTRL_C_Please = updateTimerQueue()
AudioSystem.addIndex(SoundType.SOUND_EFFECT,"./SoundFiles/funny sfx/Asterisk.wav")
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')

AudioSystem.status()
AudioSystem.unloadSoundEffectObj('sfx.name',0)
AudioSystem.status()
AudioSystem.loadSoundEffectObj("sfx.name",'Asterisk')
AudioSystem.status()

AudioSystem.toggleLoopAudioMediaSlot('mastesr',0)
AudioSystem.toggleLoopAudioMediaSlot('sfx.name',0)
AudioSystem.setSlotPlaybackSpeed

AudioSystem.addIndex(SoundType.SOUND_EFFECT, "./startup.wav")
AudioSystem.loadSoundEffectObj('sfx.name','startup')
AudioSystem.addIndex(SoundType.AUDIO_MEDIA, './startup.wav')
AudioSystem.loadAudioMedia('audio','startup')
AudioSystem.loadAudioMedia('audio','startup')
# AudioSystem.loadAudioMedia('audio','startup')
# AudioSystem.loadAudioMedia('audio','startup')
# AudioSystem.loadAudioMedia('audio','startup')
AudioSystem.loadAudioMedia('audio','startup')
AudioSystem.loadAudioMedia('audio','startup')
AudioSystem.loadAudioMedia('audio','startup')
AudioSystem.loadAudioMedia('audio1','startup')
AudioSystem.loadAudioMedia('audio1','startup')
AudioSystem.loadAudioMedia('audio1','startup')
# AudioSystem.stopAll()
AudioSystem.unloadAllMedia(SoundType.AUDIO_MEDIA)
# AudioSystem.status()
AudioSystem.unloadAudioMediaSlot('a',2)
sys.exit(APP.exec())