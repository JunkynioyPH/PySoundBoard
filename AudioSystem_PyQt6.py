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
    PLAY = 0
    PAUSE = 1
    STOP = 2
    LOOPING = 3
class isMediaLoaded(enum.Enum):
    LOADING = QMediaPlayer.MediaStatus.LoadingMedia
    LOADED = QMediaPlayer.MediaStatus.LoadedMedia
    BUFFERING = QMediaPlayer.MediaStatus.BufferingMedia
    BUFFERED = QMediaPlayer.MediaStatus.BufferedMedia
# Main Heart
class AudioManager():
    def __init__(self, device:QAudioDevice, audioGroups:dict[str, SoundType], masterVolume:int=100, initVolume=14, audioPoolSize:int=8):
        """The Main Class which holds everything about the Audio System"""
        rich.print(f"\nSupported MIME Types [QSoundEffect]:\n{QSoundEffect.supportedMimeTypes()}\n\nDetected AudioOutputs:\n{[Device.description() for Device in QMediaDevices.audioOutputs()]}\n")
        rich.print(f'Using Device: {device.description() if device is not None else 'System Default'}\n')
        self.rollingPoolIndex:dict[str, int] = {}
        self.rollOverEnabled:dict[str, bool] = {}
        self.audioPoolSize = audioPoolSize
        
        self.settings:dict[str, QAudioDevice|dict[str, int]] = {"device":device,"volume":{}}
        self.audioGroups:dict[str, SoundType] = audioGroups
        self.loopMode:dict[str, bool] = {}
        self.audioPool:dict[str, list[SoundEffect|AudioMedia]] = {}
        self.audioIndex:dict[SoundType, dict[str, str]] = {SoundType.AUDIO_MEDIA:{},SoundType.SOUND_EFFECT:{}}
        # init process
        for each in self.audioGroups:
            if not self.audioGroups.get(each) is SoundType.MASTER_VOLUME:
                self.loopMode[each] = False
                self.audioPool[each] = []
                self.settings['volume'][each] = initVolume
                if not self.audioGroups.get(each) is SoundType.SOUND_EFFECT:
                    self.rollingPoolIndex[each] = 0
                    self.rollOverEnabled[each] = False
            else:
                self.settings['volume'][each] = masterVolume
            if self.audioGroups.get(each) == SoundType.AUDIO_MEDIA:
                self.audioPool[each] = (self._generateAudioMediaPool(self.audioPoolSize))
            
            
    def _generateAudioMediaPool(self, poolCount):
        pool = []
        for count in range(0,poolCount):
            pool.append(AudioMedia(count, self.settings['device']))
        return pool    
    def _isValidPool(self, poolName:str):
        return poolName in self.audioPool
    def _isValidGroup(self, poolName:str):
        return poolName in self.audioGroups
    def _rolloverIndex(self, pool:str):
        # cursed, it makes a copy instead of like "renaming it" and referring to it
        index = self.rollingPoolIndex.get(pool)
        
        self.rollingPoolIndex[pool] += 1 if self.rollingPoolIndex.get(pool) != self.audioPoolSize else 0
        self.rollingPoolIndex[pool] = 0 if self.rollingPoolIndex.get(pool) == self.audioPoolSize else self.rollingPoolIndex.get(pool)
        return index if self.rollingPoolIndex.get(pool) < 1 else self.rollingPoolIndex.get(pool)-1
        
    # bound to break on re-write
    def status(self, cli:bool=True) -> None|tuple:
        """rich.prints out the current Status of AudioManager"""
        statusIndex:str = f"""
        [Index] [AudioMedia] : 
        {self.audioIndex[SoundType.AUDIO_MEDIA]}
        [Index] [SoundEffect] :
        {self.audioIndex[SoundType.SOUND_EFFECT]}"""
        statusAudioMediaPool = []
        for group in self.audioGroups:
            if SoundType.isMasterVolume(self.audioGroups, group): continue
            statusAudioMediaPool.append(f"        <{group}> \[{self.audioGroups.get(group)}] :\n\n")
            for item in self.audioPool.get(group):
                statusAudioMediaPool.append(f"{"        "*2}{item}\n")
            statusAudioMediaPool.append('\n')
                
        if cli:
            rich.print('++ [AudioManager STATUS] ++')
            rich.print(statusIndex)
            rich.print(f"\n        [Pool] [{self.audioGroups}] :")
            for each in statusAudioMediaPool:
                rich.print(each,end='')
            # for item2 in statusSoundEffectPool:
            #     rich.print('       ', item2)
            rich,print('Volume:',self.settings['volume'])
            rich.print('Looping:',self.loopMode)
            rich.print('Roll-Over:',self.rollOverEnabled,self.rollingPoolIndex)
            rich.print('++ -------------- ++')
        else:
            return statusAudioMediaPool, statusIndex
            # return f'AudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}'
    def togglePoolRollOver(self, poolName:str|None=None):
        if not self._isValidGroup(poolName) and poolName is not None or poolName not in self.rollOverEnabled and poolName is not None: 
            return rich.print(f'[AudioManager] [b][magenta]Toggle Pool Index Roll-over[/magenta]: [red b]Invalid AudioMedia Pool[/red b] <{poolName} : {self.audioGroups.get(poolName)}>')
        if poolName is not None:
            self.rollOverEnabled[poolName] = False if self.rollOverEnabled[poolName] else True
            rich.print(f"[AudioManager] [b][magenta]Toggle Pool Index Roll-over[/magenta]: Set ({poolName}) {self.rollOverEnabled[poolName]}")
            return
        for pool in self.rollOverEnabled:
            self.rollOverEnabled[pool] = False if self.rollOverEnabled[pool] else True
        rich.print(f"[AudioManager] [b][magenta]Toggle Pool Index Roll-over[/magenta]: Set {self.rollOverEnabled}")
        
    def setVolume(self, group:str, vol:int):
        """Set volume of specified group/pool"""
        # check if valid group
        if not self._isValidGroup(group): 
            return rich.print(f'[AudioManager] Invalid Group <{group}>')
        # update stored setting
        rich.print(f'[AudioManager] [b]Set Volume: <{group}> {vol} ', end='')
        self.settings.get('volume')[group] = vol
        # updating AudioMedia/SoundEffect
        if not SoundType.isMasterVolume(self.audioGroups, group):
            if SoundType.isSoundEffect(self.audioGroups, group):
                if len(self.audioPool.get(group)) < 1: return rich.print(f"[red b]Empty Pool[/red b]")
                for sound in self.audioPool.get(group):
                    sound.setVolume(vol/100)
            else:
                for audio in self.audioPool.get(group):
                    audio.device.setVolume(vol/100)
        rich.print(f"[green b]OK[/green b]")
            
    def setDevice(self, device:QAudioDevice, stopAll:bool=False):
        """Set Audio Output device to Specified QAudioDevice"""
        self.stopAll() if stopAll else self.pauseAll()
        self.settings['device'] = device
        for poolName in self.audioGroups:
            if not SoundType.isAudioMedia(self.audioGroups, poolName): continue
            # else if it is, do this
            for each in self.audioPool[poolName]:
                    each.device.setDevice(self.settings['device'])
            rich.print(f'[AudioManager] Set Device: <{poolName}> set to [blue b]{device.description()}[/blue b]')
        '' if stopAll else self.playAll()
    
    def audioMediaPos(self, poolName:str, index:int, formatted:bool=False):
        """Inspect position of an AudioMedia item in an AudioMedia pool"""
        if not SoundType.isAudioMedia(self.audioGroups, poolName):
            rich.print(f'[AudioManager] AudioMedia Position:[red b] Not {SoundType.AUDIO_MEDIA}')
            return f"Not {SoundType.AUDIO_MEDIA}"
        item = self.audioPool[poolName][index]
        dur, pos = round(item.duration()/1000,2), round(item.position()/1000,2)
        formattedText = f"{index}: {f"{pos} s" if pos < 60 else f"{round(pos/60,2)} min"} / {f'{dur} s' if dur < 60 else f'{round(dur/60,2)} min'}"
        return formattedText if formatted else (index, dur, pos)
    
    def addIndex(self, type:SoundType, path:str):
        """Adds the audio file's Path to the index and easily refered to using its file name"""
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
        """Remove the indexed audio file's Path from the audio index"""
        rich.print(f"[AudioManager] [red]Removed Index:[/red] ({type}) [magenta b]<{item}>[/magenta b] ", end='')
        # If it exists, ever. if not reply already unindexed
        if not self.audioIndex[type].get(item):
            return rich.print(f"[red b]OK[/red b]")
        # else, unindex
        self.audioIndex[type].pop(item)
        rich.print(f"[green b]OK[/green b]")
    
    def toggleLooping(self,  pool:str):
        rich.print(f"[AudioManager] Toggle Looping: ({pool}) [b]Looped ", end='')
        if not pool in self.loopMode: return rich.print('[red b] Invalid Pool')
        self.loopMode[pool] = False if self.loopMode[pool] else True
        rich.print(f"{self.loopMode[pool]} [green b]OK")
    
    def loadAudioMedia(self, pool:str, audioName:str, poolIndex:None|int=None):
        """Load the specified audioName into a specified or one of the available slots in a specified pool.
        
        It can also do slot roll-over if prefered, which only applies if self.rolloverEnabled == True and poolIndex == None"""
        rich.print(f"[AudioManager] [blue b]Load AudioMedia:[/blue b] ({pool}) [magenta b]<{audioName}>[/magenta b] ", end='')
        if not self._isValidGroup(pool): 
            return rich.print(f'[red b]Invalid Pool')
        if not SoundType.isAudioMedia(self.audioGroups, pool): return rich.print('[red b] NOT', SoundType.AUDIO_MEDIA)
        
        looping = int(((2**32) / 2) - 1) if self.loopMode[pool] else 1
        
        # Check if the audioName actually exist in audioIndex
        audioPath = self.audioIndex[SoundType.AUDIO_MEDIA].get(audioName)
        audioPathQUrl = QUrl.fromLocalFile(audioPath)
        
        # maybe find a way if we can add to index if not found given that audioName is a path not a name
        if not audioPath:
            return rich.print(f'[red b]NOT INDEXED[/red b]')
        
        def _setAudioMediaParams(slot:AudioMedia, source:QUrl):
                slot.setSource(source)
                slot.setLoops(looping)
                slot.device.setVolume(self.settings['volume'].get(pool)/100)
        
        # if no poolIndex is specified
        if poolIndex is None:
            # load to next available pool slot
            rich.print(f'[yellow b]Using[/yellow b] ', end='')
            for slot in self.audioPool.get(pool):
                if slot.mediaStatus() in isMediaLoaded: 
                    # rich.print(f'[cyan b][{slot.name}][/cyan b][red b]X[/red b] ', end='')
                    continue
                _setAudioMediaParams(slot, audioPathQUrl)
                return rich.print(f'[cyan b][Slot {slot.name}][/cyan b] [green b]OK[/green b]')
            else:
                # by design, this will NEVER ever be able to finish looping to all elements
                # in the case it does, assume all slots are isMediaLoaded
                # if rollOverEnabled for specific pool == True, override slot with new audioName
                if self.rollOverEnabled.get(pool):
                    index = self._rolloverIndex(pool)
                    slot = self.audioPool.get(pool)[index]
                    _setAudioMediaParams(slot, audioPathQUrl)
                    rich.print(f'[cyan b][Slot {index}][/cyan b] [yellow b]ROLL-OVER[/yellow b]')
                else:
                    rich.print('[cyan b][ROLL-OVER] [red b]DISABLED')
                    
        # if poolIndex IS specified
        else:
            slot = self.audioPool.get(pool)[poolIndex]
            _setAudioMediaParams(slot, audioPathQUrl)
            rich.print(f'[b]Set [cyan b][Slot {poolIndex}]','[green b]OK[/green b]')

        ####
        ## Reference for SoundEffect playback later
        ####
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
    
    def playAll(self):
        self._toggleAllPlaybackState(AudioPlaybackState.PLAY)
    
    def pauseAll(self):
        self._toggleAllPlaybackState(AudioPlaybackState.PAUSE)
    
    def playSlot(self, pool:str, slot:int):
        self._audioMediaControlState(pool, slot, AudioPlaybackState.PLAY)
    
    def pauseSlot(self, pool:str, slot:int):
        self._audioMediaControlState(pool, slot, AudioPlaybackState.PAUSE)
    
    def stopSlot(self, pool:str, slot:int):
        """This WILL clear AudioMedia to NoMedia as AudioMedia by design clears media EndOfFile"""
        self._audioMediaControlState(pool, slot, AudioPlaybackState.STOP)
    
    def test(self, item:str=''):
        # Reference for later, do not delete
        def _sfxDelete(pool, sound:SoundEffect):
            pool = self.audioPool.get(pool)
            pool.remove(sound)
            sys.exit()
        
        # create new instance of SoundEffect
        _ = SoundEffect(self.audioIndex[SoundType.AUDIO_MEDIA].get(item), self.settings.get('device'), self.settings['volume']['sfx.name'], 1)
        
        # add to pool and delete instance once audio finishes
        self.audioPool['sfx.name'].append(_)
        _.playingChanged.connect(lambda: _sfxDelete('sfx.name', _))
        
        rich.print("[green b]*TEST Done*")

    def _audioMediaControlState(self, pool:str, index:int, state:AudioPlaybackState):
        if not self._isValidGroup(pool): 
            return rich.print(f'AudioManager] [b]AudioMedia Controls: <{pool}> [red b]Invalid Pool')
        
        slot = self.audioPool.get(pool)[index]
        rich.print(f'[AudioManager] [b]AudioMedia Controls: ', end='')
        match state:
            case AudioPlaybackState.PLAY:
                stateColor = 'cyan b'
                slot.play()
            case AudioPlaybackState.PAUSE:
                stateColor = 'yellow b'
                slot.pause()
            case AudioPlaybackState.STOP:
                stateColor = 'red b'
                slot.stop()
        rich.print(f'<{pool}> [{stateColor}]{state}[/{stateColor}] <{slot}>')
        
     
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
                rich.print(f'[AudioManager] [green b]Playback All States: [/green b]<{pool}> [red b]{state}[/red b]')
                continue
            elif SoundType.isSoundEffect(self.audioGroups, pool) and stopSFXPool:
                rich.print(f'[AudioManager] [green b]Playback All States: [/green b]<{pool}> [yellow b]Empty SoundEffect Pool[/yellow b]')
                continue
            elif SoundType.isSoundEffect(self.audioGroups, pool) and state in (AudioPlaybackState.PAUSE, AudioPlaybackState.PLAY):
                continue
                
            # else if it's AudioMedia
            audioMediaPool:list[AudioMedia] = self.audioPool.get(pool)
            for audio in audioMediaPool:
                match state:
                    case AudioPlaybackState.PLAY:
                        stateColor = 'cyan b'
                        if audio.playbackState() == QMediaPlayer.PlaybackState.PlayingState: continue
                    case AudioPlaybackState.PAUSE:
                        stateColor = 'yellow b'
                        if audio.playbackState() == QMediaPlayer.PlaybackState.PausedState: continue
                    case AudioPlaybackState.STOP:
                        stateColor = 'red b'
                        # might come to bite me later
                        # mainly cuz stopping audio playback actually clears
                        # the source to NoMedia, unloaded. AudioMedia by design
                        if audio.mediaStatus() not in isMediaLoaded: continue
                self._audioMediaControlState(pool, audioMediaPool.index(audio), state)
                # rich.print(f'[AudioManager] Playback State: <{pool}> [{stateColor}]{state}[/{stateColor}]: <{audio}>')
            if not SoundType.isMasterVolume(self.audioGroups, pool) and not SoundType.isSoundEffect(self.audioGroups, pool):
                rich.print(f"[AudioManager] [green b]Playback All States: [/green b]<{pool}> [{stateColor}]{state}[/{stateColor}] [green b]OK")

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
        print({self.name}, 'died')
        
    def __repr__(self) -> str:
        # BufferingMedia == Media is being played.
        # EndOfMedia == Media has finished playing. Still indexed.
        return f"{self.name}:<{self.source().toString()}>:({str(self.mediaStatus()).split('.')[1]}_{f'Looped' if self.loops() > 1 else ''}{str(self.playbackState()).split('.')[1]})"
