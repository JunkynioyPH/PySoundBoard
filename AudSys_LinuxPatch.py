from PyQt6.QtMultimedia import *
from PyQt6.QtCore import QUrl
import AudioSystem_PyQt6 as AS

## Linux Fix

class AudioManager(AS.AudioManager):
    def __init__(self, device:QAudioDevice, audioVolume:int=14, soundVolume:int=14, musicPoolSize:int=8):
        self.hostRollingPoolIndex = 0
        self.hostAudioPool:list[AS.AudioMedia] = []
        self._initHostAudioPool(musicPoolSize)
        super().__init__(device, audioVolume, soundVolume, musicPoolSize)
        print('[AudioManager Patch] Linux Pipewire fix Applied')
        
    def _initHostAudioPool(self, poolCount):
        self.hostAudioPool = []
        for count in range(0,poolCount):
            _ = AS.AudioMedia(count, QMediaDevices.defaultAudioOutput())
            self.hostAudioPool.append(_)
            # _.sourceChanged.connect(lambda: print('changed'))
            
    def hostAudioPoolStatus(self) -> str:
        return f"   HostAudio:\n{self.hostAudioPool}"
    
    def _playToHost(self):
        def __play(poolItem:AS.AudioMedia, source:QUrl, volume:int, loops:int):
                poolItem.setSource(source)
                poolItem.device.setVolume(volume)
                poolItem.setLoops(loops)
                poolItem.play()
            
        if self.multiMode['audio']: # if true'
            for each in self.hostAudioPool:
                if each.mediaStatus() not in (QMediaPlayer.MediaStatus.EndOfMedia, QMediaPlayer.MediaStatus.NoMedia):
                    # print("*Empty*")
                    continue
                fromAudioPool = self.audioPool['audio'][self.hostAudioPool.index(each)]
                __play(each, fromAudioPool.source(), fromAudioPool.device.volume(), fromAudioPool.loops())
                print(f"[AudioManager Patch] (hostAudioPool) Sync PLAY to {each}")
                return
            else:
                if self.hostRollingPoolIndex == len(self.hostAudioPool):
                    self.hostRollingPoolIndex = 0
                print(f"[AudioManager Patch] (hostAudioPool) Sync PLAY <reusing> {self.hostAudioPool[self.hostRollingPoolIndex]} ")
                rollingIndex = self.hostAudioPool[self.hostRollingPoolIndex]
                fromAudioPool = self.audioPool['audio'][self.hostRollingPoolIndex]
                
                __play(rollingIndex, fromAudioPool.source(), fromAudioPool.device.volume(), fromAudioPool.loops())
                self.hostRollingPoolIndex += 1
        else:
            poolItem = self.hostAudioPool[0]
            fromAudioPool = self.audioPool['audio'][0]
            __play(poolItem, fromAudioPool.source(), fromAudioPool.device.volume(), fromAudioPool.loops())
            print(f"[AudioManager Patch] (hostAudioPool) Sync PLAY to {fromAudioPool}")
        
    def _stopAllToHost(self):
            for each in self.hostAudioPool:
                # print(f"[AudioManager Patch]  Linking {each} to {self.hostAudioPool[self.audioPool['audio'].index(each)]}")
                if each.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia:
                    continue
                each.stop()
                each.setSource(QUrl.fromLocalFile(None))
                print(f"[AudioManager Patch] (hostAudioPool) Sync STOP to  {each}")
                
    def _pauseAllToHost(self):
        for each in self.hostAudioPool:
            if each.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                continue
            each.pause()
            print(f"[AudioManager Patch] (hostAudioPool) Sync PAUSE to {each}")
            
    def _resumeAllToHost(self):
        for each in self.hostAudioPool:
            if each.playbackState() != QMediaPlayer.PlaybackState.PausedState:
                continue
            each.play()
            print(f"[AudioManager Patch] (hostAudioPool) Sync RESUME to {each}")

    def setVolume(self, type:str, vol:int):
        for each in self.hostAudioPool:
            each.device.setVolume(self.settings['volume'][type.lower()]/100)
        super().setVolume(type, vol)
    
    def play(self, type:str, item:str):
        super().play(type, item) 
        self._playToHost()
        
    def stopAll(self, type:str):
        super().stopAll(type)
        self._stopAllToHost()
        
    def pauseAll(self, type:str):
        super().pauseAll(type)
        self._pauseAllToHost()
        
    def resumeAll(self, type:str):
        super().resumeAll(type)
        self._resumeAllToHost()
        