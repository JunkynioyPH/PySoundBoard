from PyQt6.QtMultimedia import *
from PyQt6.QtCore import QUrl, QTimer
import time, os, rich, sys, enum
from rich import pretty
pretty.install()

# Sound Types
class SoundType(enum.Enum):
    MASTER_VOLUME = 0
    AUDIO_MEDIA = 1
    SOUND_EFFECT = 2
    @staticmethod
    def isType(group_item:tuple[dict, str], type:"SoundType"):
        audioGroups, poolName = group_item
        return audioGroups.get(poolName) is type
    @staticmethod
    def isAudioMedia(audioGroups:dict, poolName):
        return SoundType.isType((audioGroups, poolName), SoundType.AUDIO_MEDIA)
    @staticmethod
    def isSoundEffect(audioGroups:dict, poolName):
        return SoundType.isType((audioGroups, poolName), SoundType.SOUND_EFFECT)
    @staticmethod
    def isMasterVolume(audioGroups:dict, poolName):
        return SoundType.isType((audioGroups, poolName), SoundType.MASTER_VOLUME)
class AudioPlaybackState(enum.Enum):
    RESUME = 0
    PAUSE = 1
    STOP = 2
    LOOPING = 3
    MULTIPLE = 4
# Main Heart
class AudioManager():
    def __init__(self, device:QAudioDevice, audioGroups:dict[str, SoundType], masterVolume:int=100, initVolume=14, audioPoolSize:int=8):
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
        self.audioIndex:dict[SoundType, dict[str, str]] = {SoundType.AUDIO_MEDIA:{},SoundType.SOUND_EFFECT:{}}
        # init process
        for each in self.audioGroups:
            if not self.audioGroups.get(each) is SoundType.MASTER_VOLUME:
                self.multiMode[each] = False
                self.loopMode[each] = False
                self.audioPool[each] = []
            else:
                self.settings['volume'][each] = masterVolume
            if self.audioGroups.get(each) == SoundType.AUDIO_MEDIA:
                self.audioPool[each] = (self._generateAudioMediaPool(self.audioPoolSize))
            self.settings['volume'][each] = initVolume
            
    def _generateAudioMediaPool(self, poolCount):
        pool = []
        for count in range(0,poolCount):
            pool.append(AudioMedia(count, self.settings['device']))
        return pool    
    def _isValidPool(self, poolName:str):
        return poolName in self.audioPool
    def _isValidGroup(self, poolName:str):
        return poolName in self.audioGroups

    # bound to break on re-write
    def status(self, cli:bool=True) -> None|tuple:
        """rich.prints out the current Status of AudioManager"""
        statusIndex:str = f"""
        [Index] [AudioMedia] : 
        {self.audioIndex[SoundType.AUDIO_MEDIA]}
        [Index] [SoundEffect] :
        {self.audioIndex[SoundType.SOUND_EFFECT]}"""
        statusAudioMediaPool = [f"\[{pool}] : {self.audioPool[pool]}\n" for pool in self.audioPool if SoundType.isAudioMedia(self.audioGroups, pool)]
        statusSoundEffectPool = [f"\[{pool}] : {self.audioPool[pool]}\n" for pool in self.audioPool if SoundType.isSoundEffect(self.audioGroups, pool)]
        if cli:
            rich.print('++ [AudioManager] ++')
            rich.print(statusIndex)
            rich.print("        [Pool] [AudioMedia] : ")
            for item in statusAudioMediaPool:
                rich.print('       ', item)
            rich.print('        [Pool] [SoundEffect] : ')
            for item in statusSoundEffectPool:
                rich.print('       ', item)
            rich.print('++ -------------- ++')
        else:
            return statusAudioMediaPool, statusSoundEffectPool, statusIndex
            # return f'AudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}'

    def setVolume(self, group:str, vol:int):
        # check if valid group
        if not self._isValidGroup(group): 
            return rich.print(f'[AudioManager] Invalid Group <{group}>')
        # update stored setting
        rich.print(f'[AudioManager] Set Volume: <{group}> {vol}')
        self.settings.get('volume')[group] = vol
        # updating AudioMedia/SoundEffect
        if not SoundType.isMasterVolume(self.audioGroups, group):
            if SoundType.isSoundEffect(self.audioGroups, group):
                if len(self.audioPool.get(group)) < 1: return rich.print(f"[AudioManager] Set Volume: <{group}> [red b]Empty Pool[/red b]")
                for sound in self.audioPool.get(group):
                    sound.setVolume(vol/100)
            else:
                for audio in self.audioPool.get(group):
                    audio.device.setVolume(vol/100)
            rich.print(f"[AudioManager] Set Volume: <{group}> [green b]OK[/green b]")
            
    def setDevice(self, device:QAudioDevice, stopAll:bool=False):
        self.stopAll() if stopAll else self.pauseAll()
        self.settings['device'] = device
        for poolName in self.audioGroups:
            if not SoundType.isAudioMedia(self.audioGroups, poolName): continue
            # else if it is, do this
            for each in self.audioPool[poolName]:
                    each.device.setDevice(self.settings['device'])
            rich.print(f'[AudioManager] Set Device: <{poolName}> set to [blue b]{device.description()}[/blue b]')
        '' if stopAll else self.resumeAll()
    
    def audioMediaPos(self, poolName:str, index:int, formatted:bool=False):
        if not SoundType.isAudioMedia(self.audioGroups, poolName):
            rich.print(f'[AudioManager] AudioMedia Position:[red b] Not {SoundType.AUDIO_MEDIA}')
            return f"Not {SoundType.AUDIO_MEDIA}"
        item = self.audioPool[poolName][index]
        dur, pos = round(item.duration()/1000,2), round(item.position()/1000,2)
        formattedText = f"{index}: {f"{pos} s" if pos < 60 else f"{round(pos/60,2)} min"} / {f'{dur} s' if dur < 60 else f'{round(dur/60,2)} min'}"
        return formattedText if formatted else (index, dur, pos)
    
    def addIndex(self, type:SoundType, path:str):
        audioName:str = os.path.splitext(os.path.basename(path))[0]
        rich.print(f"[AudioManager] [green]Adding Index:[/green] ({type}) '{audioName}' [magenta b]<{path}>[/magenta b] ", end='')
        ## Normalise path
        path = os.path.join(os.curdir,path)
        if not os.path.exists(path):
            return rich.print("[red b]*Path Not Found*[/red b]")
        # Check if already indexed. If true, override name with discriminator
        if self.audioIndex[type].get(audioName):
            audioName = f"{audioName}.{len(self.audioIndex[type])^len(audioName)}"
            rich.print(f'as [blue]<{audioName}>[/blue] ', end='')
        # Index the new item
        self.audioIndex[type][audioName] = path
        rich.print(f"[green b]OK[/green b]")

    def removeIndex(self, type:SoundType, item:str):
        rich.print(f"[AudioManager] [red]Removed Index:[/red] ({type}) [magenta b]<{item}>[/magenta b] ", end='')
        # If it exists, ever. if not reply already unindexed
        if not self.audioIndex[type].get(item):
            return rich.print(f"[red b]OK[/red b]")
        # else, unindex
        self.audioIndex[type].pop(item)
        rich.print(f"[green b]OK[/green b]")
    
     # reimplement to use the new audioGroups
    def toggleState(self,  pool:str, mode:AudioPlaybackState):
        rich.print(f"[AudioManager] ToggleState: ({pool}) [b]{mode} ", end='')
        if not type not in (AudioPlaybackState.LOOPING, AudioPlaybackState.MULTIPLE):
            rich.print("[red b]Invalid mode")
            return 
        if mode is AudioPlaybackState.LOOPING:
            if not pool in self.loopMode: return rich.print('[red b] Invalid Pool')
            self.loopMode[pool] = True if self.loopMode[pool] is False else False
        if mode is AudioPlaybackState.MULTIPLE:
            if not pool in self.multiMode: return rich.print('[red b] Invalid Pool')
            self.multiMode[pool] = True if self.multiMode[pool] is False else False
        rich.print("[green b]OK")
    
    ########################## bound to break on re-write
    ########### Rewrite to use new type checking
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
        if self.audioPool['sound'] != [] and self.multiMode['sound'] == False:
            self.audioPool['sound'][0].stop()
        
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
        def _playAudioMedia(poolItem:AudioMedia, Source:QUrl, volume:int, loops:int):
            poolItem.setSource(Source)
            poolItem.setLoops(loops)
            poolItem.device.setVolume(volume)
            poolItem.play()
        def _sfxDelete(pool, sound:SoundEffect):
            pool = self.audioPool.get(pool)
            pool.remove(sound)
            # self.stopAll()
            sys.exit()
        # create new instance of SoundEffect
        # _ = SoundEffect(self.audioIndex[SoundType.AUDIO_MEDIA].get(item), self.settings.get('device'), self.settings['volume']['sfx.name'], 1)
        _playAudioMedia(self.audioPool['music'][3], QUrl.fromLocalFile(self.audioIndex[SoundType.AUDIO_MEDIA].get(item)), self.settings['volume'].get('music'),1)
        # add to pool and delete instance once audio finishes
        # self.audioPool['sfx.name'].append(_)
        # _.playingChanged.connect(lambda: _sfxDelete('sfx.name', _))
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
                rich.print(f'[AudioManager] <{pool}> [red b]{state}[/red b] [green b]OK[/green b]')
                continue
            elif SoundType.isSoundEffect(self.audioGroups, pool) and stopSFXPool:
                rich.print(f'[AudioManager] <{pool}> [yellow b]Empty SoundEffect Pool[/yellow b] [green b]OK[/green b]')
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
