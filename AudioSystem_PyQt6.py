from PyQt6.QtMultimedia import *
from PyQt6.QtCore import QUrl, QTimer
from xpfpath import xpfp
import time, os, rich, sys, enum
from rich import pretty
pretty.install()

# Sound Types
class SoundType(enum.Enum):
    MASTER_VOLUME = 0
    AUDIO_MEDIA = 1
    SOUND_EFFECT = 2
    @staticmethod
    def isAudioMedia(audioGroups:dict, _poolname):
        # print(f"{audioGroups.get(_poolname) == SoundType.AUDIO_MEDIA} {_poolname}")
        if audioGroups.get(_poolname) == SoundType.AUDIO_MEDIA: return True
        else: return False
    @staticmethod
    def isSoundEffect(audioGroups:dict, _poolname):
        # print(f"{audioGroups.get(_poolname) == SoundType.SOUND_EFFECT} {_poolname}")
        if audioGroups.get(_poolname) == SoundType.SOUND_EFFECT: return True
        else: return False
    @staticmethod
    def isMasterVolume(audioGroups:dict, _poolname):
        # print(f"{audioGroups.get(_poolname) == SoundType.SOUND_EFFECT} {_poolname}")
        if audioGroups.get(_poolname) == SoundType.MASTER_VOLUME: return True
        else: return False
class AudioPlaybackState(enum.Enum):
    RESUME = 0
    PAUSE = 1
    STOP = 2
# Main Heart
class AudioManager():
    def __init__(self, device:QAudioDevice, audioGroups:dict[str, SoundType], masterVolume:int=100, audioVolume:int=14, soundVolume:int=14, audioPoolSize:int=8):
        """The Main Class which holds everything about the Audio System"""
        rich.print(f"\nSupported MIME Types [QSoundEffect]:\n{QSoundEffect.supportedMimeTypes()}\n\nDetected AudioOutputs:\n{[Device.description() for Device in QMediaDevices.audioOutputs()]}\n")
        rich.print(f'Using Device: {device.description() if device is not None else 'System Default'}\n')
        self.rollingPoolIndex:int = 0
        self.audioPoolSize = audioPoolSize
        
        # 'audio':audioVolume,'sound':soundVolume
        self.settings:dict[str, QAudioDevice|dict[str, int]] = {"device":device,"volume":{}}
        self.audioGroups:dict[str, SoundType] = audioGroups
        self.multiMode:dict[str, bool] = {}
        self.loopMode:dict[str, bool] = {}
        self.audioPool:dict[str, list[SoundEffect|AudioMedia]] = {}
        self.audioIndex:dict[str, dict[str, str]] = {'audio':{},'sound':{}}
        # init process
        for each in self.audioGroups:
            if self.audioGroups.get(each) != SoundType.MASTER_VOLUME:
                self.multiMode[each] = False
                self.loopMode[each] = False
                self.audioPool[each] = []
            else:
                self.settings['volume'][each] = masterVolume
            if self.audioGroups.get(each) == SoundType.AUDIO_MEDIA:
                self.audioPool[each] = (self._generateAudioMediaPool(self.audioPoolSize))
                self.settings['volume'][each] = audioVolume
            elif self.audioGroups.get(each) == SoundType.SOUND_EFFECT:
                self.settings['volume'][each] = soundVolume
            
        
    
    def _generateAudioMediaPool(self, poolCount):
        pool = []
        for count in range(0,poolCount):
            pool.append(AudioMedia(count, self.settings['device']))
        return pool
    
    # make it use SoundType
    def _isValidType(self, type:str):
        if type.lower() not in ('audio','sound'):
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        
    def _isValidPool(self, poolName:str):
        if poolName not in self.audioPool:
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        
    def _isValidMode(self, mode:str):
        if mode.lower() not in ('multi','loop'):
            return rich.print('*Unknown Mode*')

    # # bound to break on re-write
    # def status(self, cli:bool=True) -> None|str:
    #     """rich.prints out the current Status of AudioManager"""
    #     status:str = f"...Index..:\n   Audio: {self.audioIndex['audio']}\n   Sound: {self.audioIndex['sound']}\n\nAudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}"
    #     if cli:
    #         rich.print('++ [AudioManager] ++')
    #         rich.print(status)
    #         rich.print('++ -------------- ++')
    #     else:
    #         return f'AudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}'
    
    ##################### Bound to break
    def setVolume(self, type:str, vol:int):
        # Check if type exist
        self._isValidType(type.lower())
        
        # update AudioManager Setting
        self.settings['volume'][type.lower()] = vol
        # self.stopAll('sound') if type.lower() == 'sound' else self.pauseAll('audio')
        for each in self.audioPool[type.lower()]:
            if type.lower() == 'sound':
                each.setVolume(self.settings['volume'][type.lower()]/100)
            else:
                each.device.setVolume(self.settings['volume'][type.lower()]/100)
            
    def setDevice(self, device:QAudioDevice, stopAll:bool=False):
        self.stopAll() if stopAll else self.pauseAll()
        self.settings['device'] = device
        
        # Take into account already playing SoundType.isSoundEffect()
        for _poolName in self.audioGroups:
            if SoundType.isMasterVolume(self.audioGroups, _poolName): continue
            # else if it is, do this
            for each in self.audioPool[_poolName]:
                if SoundType.isAudioMedia(self.audioGroups, _poolName):
                    each.device.setDevice(self.settings['device'])
                else:
                    each.setAudioDevice(self.settings['device'])
            rich.print(f'[AudioManager] Set Device: <{_poolName}> set to [blue b]{device.description()}[/blue b]')
        
        '' if stopAll else self.resumeAll()
    
    # needs check to restrict to AudioMedia objects only!
    def audioMediaPos(self, poolName:str, index:int):
        item = self.audioPool[poolName][index]
        dur, pos = round(item.duration()/1000,2), round(item.position()/1000,2)
        return f"{index}: {f"{pos} s" if pos < 60 else f"{round(pos/60,2)} min"} / {f'{dur} s' if dur < 60 else f'{round(dur/60,2)} min'}"
    
    # reimplement to use SoundType
    def addIndex(self, type:str, path:str):
        audioName:str = os.path.splitext(os.path.basename(path))[0]
        rich.print(f"[AudioManager] [green]Adding Index:[/green] ({type}) '{audioName}' [magenta b]<{path}>[/magenta b] ", end='')
        
        ## Normalise path to have ' ./ , .\\ ' prefix
        ## In windows, this check will fail and duplicate " .\\ "
        ## However, " .\\.\\ " will still point to "Current Directory"
        ## I Should probably use "os.path" stuff for this instead of xpfp() shit thing i made
        path = path if xpfp('./') in path else xpfp(f'./{path}')
        if not os.path.exists(path):
            return rich.print("[red b]*Path Not Found*[/red b]")
        
        # Check if type exist
        self._isValidType(type.lower())
        
        # Check if key exist in dict, say it's a duplicate if it is, and append disriminator
        if  self.audioIndex[type.lower()].get(audioName):
            audioName = f"{audioName}.{len(self.audioIndex['audio'])^len(audioName)}"
            rich.print(f'as [blue]<{audioName}>[/blue] ', end='')
        
        # else, make key
        if type.lower() == 'audio':
            self.audioIndex['audio'][audioName] = path
            rich.print(f"[green b]*Added Index*[/green b]")
        else:
            self.audioIndex['sound'][audioName] = path
            rich.print(f"[green b]*Added Index*[/green b]")
    
    # reimplement to use SoundType
    def removeIndex(self, type:str, item:str):
        rich.print(f"[AudioManager] [red]Removed Index:[/red] ({type}) [magenta b]<{item}>[/magenta b] ", end='')
        # Check if type exist
        self._isValidType(type.lower())
        
        # If it exists, ever. if not reply already unindexed
        if not self.audioIndex.get(type.lower()) and not self.audioIndex[type.lower()].get(item):
            return rich.print(f"[red b]*Already Removed Index*[/red b]")

        # else, unindex
        if type.lower() == 'audio':
            self.audioIndex['audio'].pop(item)
            rich.print(f"[red b]*Removed Index*[/red b]")
        else:
            self.audioIndex['sound'].pop(item)
            rich.print(f"[red b]*Removed Index*[/red b]")
    
     # reimplement to use the new audioGroups
    def toggleState(self, type:str, mode:str):
        rich.print(f"[AudioManager] ToggleState: ({type}) '{mode}' ", end='')
        
        self._isValidType(type.lower())
        self._isValidMode(mode.lower())
        
        if mode.lower() == 'multi':
            self.multiMode[type.lower()] = True if self.multiMode[type.lower()] != True else False
            rich.print(f"{self.multiMode[type.lower()]} ", end='')
        else:
            self.loopMode[type.lower()] = True if self.loopMode[type.lower()] != True else False
            rich.print(f"{self.loopMode[type.lower()]} ", end='')
        rich.print("*Done*")
    
    ########################## bound to break on re-write
    def load(self, type:str, item:str):
        rich.print(f"[AudioManager] [blue b]Play:[/blue b] ({type}) [magenta b]<{item}>[/magenta b] ", end='')
        
        looping = int(((2**32) / 2) - 1) if self.loopMode[type.lower()] else 1
        
        # Check if type exist in the list
        self._isValidType(type.lower())
        # Check if the audio actually exist in audioIndex
        audioName = self.audioIndex[type.lower()].get(item)
        if not audioName:
            return rich.print(f'[red b]*Not Found*[/red b]')
        
        # if it's not empty, something is already playing, remove it and proceed
        # else add to pool
        # if self.audioPool['sound'] != [] and self.multiMode['sound'] == False:
        #     self.audioPool['sound'][0].stop()
        
        # clean up after sound is done playing
        def _sfxDelete(pool, sound:SoundEffect):
            # if sound.pauseState:
            #     return
            pool = self.audioPool.get(pool)
            pool.remove(sound)
        
        # shorten
        def _playAudioMedia(poolItem:AudioMedia, Source:QUrl, volume:int, loops:int):
            poolItem.setSource(Source)
            poolItem.setLoops(loops)
            poolItem.device.setVolume(volume)
            poolItem.play()
            
        # if type.lower() == 'audio':
        #     if self.multiMode['audio']: # if true'
        #         for poolItem in self.audioPool['audio']:
                    
        #             # Skip if it's not EndOfMedia | NoMedia
        #             if poolItem.mediaStatus() not in (QMediaPlayer.MediaStatus.EndOfMedia, QMediaPlayer.MediaStatus.NoMedia):
        #                 # != EndOfMedia|NoMedia
        #                 # In the event that all of the pool are in use, this will
        #                 # actually finish the rest of iteration and
        #                 # trigger the 'else' statement below.
        #                 continue
                    
        #             #
        #             # parameters:
        #             # QUrl.fromLocalFile(self.audioIndex['audio'].get(item))
        #             # self.settings['volume']['audio']/100
        #             #
        #             # if it's EndOfMedia | NoMedia AND StoppedState
        #             _playAudioMedia(poolItem, QUrl.fromLocalFile(self.audioIndex['audio'].get(item)), self.settings['volume']['audio']/100, looping)
        #             rich.print('*Done*')
        #             return
        #         else:
        #             if self.rollingPoolIndex == len(self.audioPool['audio']):
        #                 self.rollingPoolIndex = 0
        #             rich.print(f"[yellow b]<reusing> {self.audioPool['audio'][self.rollingPoolIndex]}[/yellow b] ", end='')
        #             rollingIndex = self.audioPool['audio'][self.rollingPoolIndex]
        #             _playAudioMedia(rollingIndex, QUrl.fromLocalFile(self.audioIndex['audio'].get(item)), self.settings['volume']['audio']/100, looping)
        #             self.rollingPoolIndex += 1
        #     else:
        #         poolItem = self.audioPool['audio'][0]
        #         _playAudioMedia(poolItem, QUrl.fromLocalFile(self.audioIndex['audio'].get(item)), self.settings['volume']['audio']/100, looping)
        #     rich.print('*Done*')
        # else:
        #     if self.multiMode['sound']:
        #         # create new instance of SoundEffect
        #         _ = SoundEffect(self.audioIndex['sound'].get(item), self.settings['device'], self.settings['volume']['sound'], looping)

        #         # add to pool and delete instance once audio finishes
        #         self.audioPool['sound'].append(_)
        #         _.playingChanged.connect(lambda: _vanish(_))
        #         rich.print("*Done*")
        #     else:
        #         _ = SoundEffect(self.audioIndex['sound'].get(item), self.settings['device'], self.settings['volume']['sound'], looping)
        #         if self.audioPool['sound'] != []:
        #             self.audioPool['sound'][0].stop()
        #             self.audioPool['sound'].append(_)
        #         else:
        #             self.audioPool['sound'].append(_)
        #         _.playingChanged.connect(lambda: _vanish(_))
        #         rich.print("*Done*")
    
    def stopAll(self):
        self._toggleAllPlaybackState(AudioPlaybackState.STOP)
    
    def resumeAll(self):
        self._toggleAllPlaybackState(AudioPlaybackState.RESUME)
    
    def pauseAll(self):
        self._toggleAllPlaybackState(AudioPlaybackState.PAUSE)
        
    def test(self, item:str):
        def _sfxDelete(pool, sound:SoundEffect):
            # pool = self.audioPool.get(pool)
            # pool.remove(sound)
            # self.stopAll()
            sys.exit()
        # create new instance of SoundEffect
        _ = SoundEffect(self.audioIndex['audio'].get(item), self.settings['device'], self.settings['volume']['sfx.name'], 1)

        # add to pool and delete instance once audio finishes
        self.audioPool['sfx.name'].append(_)
        _.playingChanged.connect(lambda: _sfxDelete('sfx.name', _))
        rich.print("[green b]*TEST Done*")
        
    def _toggleAllPlaybackState(self, state:AudioPlaybackState):
        for pool in self.audioGroups:
            # print(state, pool)
            if SoundType.isMasterVolume(self.audioGroups, pool): continue
            
            # stopping SFX
            stopSFXPool = True if state == AudioPlaybackState.STOP else False
            if SoundType.isSoundEffect(self.audioGroups, pool) and len(self.audioPool.get(pool)) != 0 and stopSFXPool:
                soundEffectPool:list[SoundEffect] = self.audioPool.get(pool)
                for sound in soundEffectPool:
                    sound.stop()
                rich.print(f'[AudioManager] <{pool}> [b]{SoundType.SOUND_EFFECT}[/b] [red b]{state}[/red b] [green b]OK[/green b]')
                continue
            elif SoundType.isSoundEffect(self.audioGroups, pool) and stopSFXPool:
                rich.print(f'[AudioManager] <{pool}> [b]{SoundType.SOUND_EFFECT}[/b] [red b]Empty Pool[/red b] [green b]OK[/green b]')
                continue
            elif SoundType.isSoundEffect(self.audioGroups, pool) and state in (AudioPlaybackState.PAUSE, AudioPlaybackState.RESUME):
                continue
                
            # else if it's AudioMedia
            audioMediaPool:list[AudioMedia] = self.audioPool.get(pool)
            for audio in audioMediaPool:
                match state:
                    case AudioPlaybackState.RESUME:
                        stateColor = 'cyan b'
                        if audio.playbackState() != QMediaPlayer.PlaybackState.PausedState: continue
                        audio.play()
                    case AudioPlaybackState.PAUSE:
                        stateColor = 'yellow b'
                        if audio.playbackState() != QMediaPlayer.PlaybackState.PlayingState: continue
                        audio.pause()
                    case AudioPlaybackState.STOP:
                        stateColor = 'red b'
                        if audio.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia: continue
                        audio.stop()
                rich.print(f'[AudioManager] [{stateColor}]{state}[/{stateColor}]: <{audio}>')
            if not SoundType.isMasterVolume(self.audioGroups, pool) and not SoundType.isSoundEffect(self.audioGroups, pool):
                rich.print(f"[AudioManager] <{pool}> [{stateColor}]{state}[/{stateColor}] [green b]OK[/green b]")

class SoundEffect(QSoundEffect):
    def __init__(self, file:str, device:QAudioDevice, volume:int, loops:int):
        super().__init__()
        self.name = os.path.basename(file)
        self.setAudioDevice(device)
        self.setSource(QUrl.fromLocalFile(file))
        self.setVolume(volume/100)
        self.setLoopCount(loops)
        self.play()
        
    def __repr__(self) -> str:
        return f"{self.name}{' (looped)' if self.loopCount() > 1 else ''}"
###
#  Plan to add PlaybackRate. maybe slowmo, or fast-mo functions.
###
#  Plan to add a slight delay when playing and unindexing Media,
#  in the hopes that it would reduce or eliminate crackles when playing audio
###
class AudioMedia(QMediaPlayer):
    def __init__(self, count, device:QAudioDevice):
        super().__init__()
        self.name = count
        self.device = QAudioOutput(device)
        self.setAudioOutput(self.device)
        self.mediaStatusChanged.connect(self._clearMedia)
    
    def _clearMedia(self):
        # is it EndOfMedia?
        if self.mediaStatus() != QMediaPlayer.MediaStatus.EndOfMedia:
            return
        # clear itself
        self.setSource(QUrl(QUrl.fromLocalFile(None)))
        
    def __repr__(self) -> str:
        # BufferingMedia == Media is being played.
        # EndOfMedia == Media has finished playing. Still indexed.
        return f"{self.name}:<{self.source().toString()}>:({str(self.mediaStatus()).split('.')[1]}_{f'Looped' if self.loops() > 1 else ''}{str(self.playbackState()).split('.')[1]})"
