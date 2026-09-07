from PyQt6.QtMultimedia import *
from PyQt6.QtCore import QUrl
import os, rich, enum
from rich import pretty
pretty.install()
# Sound Types
class SoundType(enum.Enum):
    """MASTER_VOLUME is just a Dummy, for front-end to use to scale volumes to other sound Types"""
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
class AudioPlaybackAction(enum.Enum):
    PLAY = 0
    PAUSE = 1
    STOP = 2
    LOOPING = 3
class MediaLoaded(enum.Enum):
    """Use def contains(cls, status): to compare .mediastatus():QMediaPlayer.MediaStatus and this class' Values."""
    LOADING = QMediaPlayer.MediaStatus.LoadingMedia
    LOADED = QMediaPlayer.MediaStatus.LoadedMedia
    BUFFERING = QMediaPlayer.MediaStatus.BufferingMedia
    BUFFERED = QMediaPlayer.MediaStatus.BufferedMedia
    ENDOFMEDIA = QMediaPlayer.MediaStatus.EndOfMedia
    @classmethod
    def contains(cls, status):
        try:
            cls(status)
            return True
        except ValueError:
            return False
class PlaybackStatus(enum.Enum):
    """Use PlaybackStatus.Playing.value to compare .playbackstate():QMediaPlayer.PlaybackState and this class' Values."""
    PLAYING = QMediaPlayer.PlaybackState.PlayingState
    PAUSED = QMediaPlayer.PlaybackState.PausedState
    STOPPED = QMediaPlayer.PlaybackState.StoppedState
class AudioManager():
    def __init__(self, device:QAudioDevice, audioGroups:dict[str, SoundType], masterVolume:int=100, initVolume=14, audioPoolSize:int=8):
        """The Main Class which holds everything about the Audio System"""
        rich.print(f'[AudioManager] Using Device: {device.description() if device is not None else 'System Default'}')
        self.rollingPoolIndex:dict[str, int] = {}
        self.rollOverEnabled:dict[str, bool] = {}
        self.audioPoolSize = audioPoolSize
        self.settings:dict[str, QAudioDevice|dict[str, int]] = {"device":device,"volume":{}}
        self.audioGroups:dict[str, SoundType] = audioGroups
        self.audioPool:dict[str, list[SoundEffect|AudioMedia]] = {}
        self.audioIndex:dict[SoundType, dict[str, str]] = {SoundType.AUDIO_MEDIA:{},SoundType.SOUND_EFFECT:{}}
        self.isType = self.isTypeCheck(self)
        # init process
        for each in self.audioGroups:
            if not self.audioGroups.get(each) is SoundType.MASTER_VOLUME:
                self.audioPool[each] = []
                self.settings['volume'][each] = initVolume
                if not self.audioGroups.get(each) is SoundType.SOUND_EFFECT:
                    self.rollingPoolIndex[each] = 0
                    self.rollOverEnabled[each] = False
            else:
                self.settings['volume'][each] = masterVolume
            if self.audioGroups.get(each) == SoundType.AUDIO_MEDIA:
                self.audioPool[each] = (self._generateAudioMediaPool(self.audioPoolSize))
    # YAAAY MORE BOILER PLATE!!!!!!!!
    class isTypeCheck:
        def __init__(self, progenitor:AudioManager):
            self.groups = progenitor.audioGroups
        def audioMedia(self, pool) -> bool:
            return SoundType.isAudioMedia(self.groups, pool)
        def soundEffect(self, pool) -> bool:
            return SoundType.isSoundEffect(self.groups, pool)
        def masterVolume(self, pool) -> bool:
            return SoundType.isMasterVolume(self.groups, pool)
    def _generateAudioMediaPool(self, poolCount):
        pool = []
        for count in range(0,poolCount):
            pool.append(AudioMedia(count, self.settings['device']))
        return pool
    # ### What the actual fook is this and what is it for
    # ### going to comment it out see if it breaks anything in the future
    # ### this checks groups with MASTER VOL types omitted
    # def _isValidPool(self, poolName:str):
    #     return poolName in self.audioPool
    # This checks groups with MASTER VOL types
    def _isValidGroup(self, poolName:str):
        return poolName in self.audioGroups
    def _rolloverIndex(self, pool:str):
        # cursed, it makes a copy instead of like "renaming it" and referring to it
        index = self.rollingPoolIndex.get(pool)
        self.rollingPoolIndex[pool] += 1 if self.rollingPoolIndex.get(pool) != self.audioPoolSize else 0
        self.rollingPoolIndex[pool] = 0 if self.rollingPoolIndex.get(pool) == self.audioPoolSize else self.rollingPoolIndex.get(pool)
        return index if self.rollingPoolIndex.get(pool) < 1 else self.rollingPoolIndex.get(pool)-1
    def status(self, cli:bool=True) -> None|tuple:
        """rich.prints out the current Status of AudioManager"""
        statusIndex:str = f"""
        [Index] [AudioMedia] : 
        {self.audioIndex[SoundType.AUDIO_MEDIA]}
        [Index] [SoundEffect] :
        {self.audioIndex[SoundType.SOUND_EFFECT]}"""
        statusAudioMediaPool = []
        # CLI text formatting
        for pool in self.audioGroups:
            print
            if SoundType.isMasterVolume(self.audioGroups, pool): continue
            statusAudioMediaPool.append(f"        <{pool}> {self.audioGroups.get(pool)} :\n")
            pool_content = self.audioPool.get(pool)
            for item in pool_content:
                statusAudioMediaPool.append(f"{"    "*4}[{pool_content.index(item)}] {item}\n")
            statusAudioMediaPool.append('\n')
        # CLI text out or return tuple
        if cli:
            rich.print('++ [AudioManager STATUS] ++')
            rich.print(statusIndex)
            rich.print(f"\n        [Pool] [{self.audioGroups}] :")
            for each in statusAudioMediaPool:
                rich.print(each,end='')
            rich.print('Volume:',self.settings['volume'])
            rich.print('Slots Roll-Over:',self.rollOverEnabled,self.rollingPoolIndex)
            rich.print('++ -------------- ++')
        else:
            return statusAudioMediaPool, statusIndex, self.rollOverEnabled, self.rollingPoolIndex
            # return f'AudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}'
    def togglePoolRollOver(self, poolName:str|None=None):
        rich.print(f'[AudioManager] [b][magenta]Index Roll-over:[/magenta] ', end='')
        if poolName not in self.rollOverEnabled and poolName is not None: 
            return rich.print(f'<{poolName}: {self.audioGroups.get(poolName)}> [red b]Invalid AudioMedia Pool[/red b] ')
        if poolName is not None:
            self.rollOverEnabled[poolName] = False if self.rollOverEnabled[poolName] else True
            rich.print(f"({poolName}) [b]Set to {self.rollOverEnabled[poolName]}")
            return
        for pool in self.rollOverEnabled:
            self.rollOverEnabled[pool] = False if self.rollOverEnabled[pool] else True
        rich.print(f"[b]Toggle Pools {self.rollOverEnabled}")
    def setVolume(self, pool:str, vol:int):
        """Set volume of specified pool/pool"""
        # check if valid pool
        if not self._isValidGroup(pool): 
            return rich.print(f'[AudioManager] Invalid Group <{pool}>')
        # update stored setting
        rich.print(f'[AudioManager] [b]Set Volume: <{pool}> {vol} ', end='')
        self.settings.get('volume')[pool] = vol
        # updating AudioMedia/SoundEffect
        if not SoundType.isMasterVolume(self.audioGroups, pool):
            if SoundType.isSoundEffect(self.audioGroups, pool):
                if len(self.audioPool.get(pool)) < 1: return rich.print(f"[red b]Empty Pool[/red b]")
                for sound in self.audioPool.get(pool):
                    sound.setVolume(vol/100)
            else:
                for audio in self.audioPool.get(pool):
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
            rich.print(f'[AudioManager] [b]AudioMedia Position:[red b] ({poolName}) Not {SoundType.AUDIO_MEDIA}')
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
        ## Assume files are in same folder as executed file
        path = os.path.join(os.curdir,path)
        # for SoundEffect, if .wav
        fileExtension:str = os.path.splitext(path)[-1]
        ######## This explicit check for .wav needs to changem somehow ########
        if not fileExtension.lower().endswith('wav') and type is SoundType.SOUND_EFFECT:
            rich.print(f'[b]{fileExtension}[red] NOT SUPPORTED')
            rich.print(f'[AudioManager] [green b]Supported MimeTypes:[/green b] {QSoundEffect.supportedMimeTypes()}')
            return 
        if not os.path.exists(path):
            return rich.print("[red b]NOT FOUND[/red b]")
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
    def toggleLoopAudioMediaSlot(self, pool:str, slot:int):
        rich.print(f"[AudioManager] Toggle AudioMedia Loop: ({pool}) ", end='')
        if not self._isValidGroup(pool):
            return rich.print(f'[red b]Invalid Pool')
        if not self.isType.audioMedia(pool):
            return rich.print(f'[red b]{pool} NOT Type {SoundType.AUDIO_MEDIA}')
        slotItem = self.audioPool.get(pool)[slot]
        originalPlayingState = slotItem.playbackState()
        slotItem_currentPos = slotItem.position()
        slotItem.stop()
        slotItem.setLoops(int(((2**32) / 2) - 1) if slotItem.loops() <= 1 else 1)
        slotItem.setPosition(slotItem_currentPos)
        slotItem.pause() if originalPlayingState != PlaybackStatus.PLAYING.value else slotItem.play()
        del slotItem_currentPos
        rich.print(f"Set to {slotItem.loops() >= 2} {self.audioPool.get(pool)[slot]}")
    def loadAudioMedia(self, pool:str, audioName:str, poolIndex:None|int=None):
        """Load the specified audioName into a specified or one of the available slots in a specified pool.
        It can also do slot roll-over if prefered, which only applies if self.rolloverEnabled == True and poolIndex == None"""
        rich.print(f"[AudioManager] [blue b]Load AudioMedia:[/blue b] ({pool}) [magenta b]<{audioName}>[/magenta b] ", end='')
        if not self._isValidGroup(pool): 
            return rich.print(f'[red b]Invalid Group')
        if not self.isType.audioMedia(pool):
            return rich.print('[red b] NOT', SoundType.AUDIO_MEDIA)
        # looping = int(((2**32) / 2) - 1) if self.loopMode[pool] else 1
        # Check if the audioName actually exist in audioIndex
        audioPath = self.audioIndex[SoundType.AUDIO_MEDIA].get(audioName)
        audioPathQUrl = QUrl.fromLocalFile(audioPath)
        # maybe find a way if we can add to index if not found given that audioName is a path not a name
        if not audioPath:
            return rich.print(f'[red b]NOT INDEXED[/red b]')
        def _setAudioMediaParams(slot:AudioMedia, source:QUrl):
                slot.setSource(source)
                slot.device.setVolume(self.settings['volume'].get(pool)/100)
        # if no poolIndex is specified
        if poolIndex is None:
            # load to next available pool slot
            rich.print(f'[yellow b]Using[/yellow b] ', end='')
            for slot in self.audioPool.get(pool):
                if MediaLoaded.contains(slot.mediaStatus()): 
                    # rich.print(f'[cyan b][{slot.name}][/cyan b][red b]X[/red b] ', end='')
                    continue
                _setAudioMediaParams(slot, audioPathQUrl)
                return rich.print(f'[cyan b][Slot {slot.name}][/cyan b] [green b]OK[/green b]')
            else:
                # by design, this will NEVER ever be able to finish looping to all elements
                # in the case it does, assume all slots are MediaLoaded
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
    def unloadAllAudioMedia(self, type:SoundType|None=None):
        for pool in self.audioPool:
            if self.audioGroups.get(pool) is SoundType.SOUND_EFFECT: continue
            rich.print(f"[AudioManager] [red b]Unload All AudioMedia:[/red b] ({pool}) [blue]Slots[/blue] ",end='')
            for slot in self.audioPool.get(pool):
                if not self.audioGroups.get(pool) is SoundType.SOUND_EFFECT:
                    if not MediaLoaded.contains(slot.mediaStatus()): continue
                slot.setSource(QUrl.fromLocalFile(None))
                rich.print(f"[yellow b]{slot.name}", end=' ')
            else:
                rich.print(f"[green]OK")
        else:
            rich.print(f"[AudioManager] [red b]Unload AudioMedia:[/red b] ({type if type is not None else "ALL"}) Slots Unloaded!",)
    def unloadAudioMediaSlot(self, pool:str, poolIndex:None|int=None):
        rich.print(f"[AudioManager] [red b]Unload AudioMedia Slot:[/red b] ({pool}) ", end='')        
        if not self._isValidGroup(pool): 
            return rich.print(f'[red b]Invalid Group]')
        if not self.isType.audioMedia(pool): return rich.print('[red b]NOT', SoundType.AUDIO_MEDIA)
        rich.print(f"[magenta b]{self.audioPool[pool][poolIndex]}[/magenta b]")
        slot:AudioMedia = self.audioPool.get(pool)[poolIndex]
        slot.setSource(QUrl.fromLocalFile(None))
    
    def setSlotPlaybackSpeed(self, pool:str, slot:int, rate:float):
            slot:AudioMedia = self.audioPool.get(pool)[slot]
            rich.print(f"[AudioManager] [blue b]Playback Rate:[/blue b] ({pool}) ", end='')
            slot.setPlaybackRate(rate)
            rich.print(f'[b]Set Rate [purple]{rate}x [cyan b][Slot {slot}]','[green b]OK[/green b]')
    def stopAll(self):
        self._toggleAllPlaybackState(AudioPlaybackAction.STOP)
    def playAll(self):
        self._toggleAllPlaybackState(AudioPlaybackAction.PLAY)
    def pauseAll(self):
        self._toggleAllPlaybackState(AudioPlaybackAction.PAUSE)
    def playSlot(self, pool:str, slot:int):
        self._audioMediaControlState(pool, slot, AudioPlaybackAction.PLAY)
    def pauseSlot(self, pool:str, slot:int):
        self._audioMediaControlState(pool, slot, AudioPlaybackAction.PAUSE)
    def stopSlot(self, pool:str, slot:int):
        self._audioMediaControlState(pool, slot, AudioPlaybackAction.STOP)
    ## TODO need rework and testing to best align with AudioMedia()
    def loadSoundEffectObj(self, pool:str, sound:str):
        rich.print(f"[AudioManager] [blue b]Load SoundEffect:[/blue b] ({pool}) [magenta b]<{sound}>[/magenta b] ", end='')
        # if exists in pool
        if not self._isValidGroup(pool): 
            return rich.print(f'[red b]Invalid Group')
        # if it's SoundEffect pool
        if not self.isType.soundEffect(pool):
            return rich.print('[red b] NOT', SoundType.SOUND_EFFECT)
        # get path, and check if indexed
        sound = self.audioIndex[SoundType.SOUND_EFFECT].get(sound)
        if not sound:
            rich.print(f'[red b]NOT INDEXED[/red b]')
            return 
        soundObj = SoundEffect(sound, self.settings.get('device')) # looping
        soundObj.setVolume(self.settings['volume'][pool])
        # add to pool
        self.audioPool[pool].append(soundObj)
        rich.print(f'[green b]OK')
    # testing to best align with AudioMedia()
    def unloadSoundEffectObj(self, pool:str, index:int):
        rich.print(f"[AudioManager] [red b]Unload SoundEffect:[/red b] ({pool}) [purple]{index}_{self.audioPool[pool][index]}[/purple] ", end='')
        if not SoundType.isSoundEffect(self.audioGroups, pool):
            return rich.print('[red b] NOT', SoundType.SOUND_EFFECT)
        self.audioPool[pool].pop(index)
        rich.print(f"[green b]OK")
    def _audioMediaControlState(self, pool:str, index:int, state:AudioPlaybackAction):
        if not self._isValidGroup(pool): 
            return rich.print(f'AudioManager] [b]AudioMedia Control: <{pool}> [red b]Invalid Pool')
        slot = self.audioPool.get(pool)[index]
        rich.print(f'[AudioManager] [b]AudioMedia Control: ', end='')
        match state:
            case AudioPlaybackAction.PLAY:
                stateColor = 'cyan b'
                slot.play()
            case AudioPlaybackAction.PAUSE:
                stateColor = 'yellow b'
                slot.pause()
            case AudioPlaybackAction.STOP:
                stateColor = 'red b'
                slot.stop()
        rich.print(f'<{pool}> [{stateColor}]{state}[/{stateColor}] [purple]{slot}[/purple]')
    def _toggleAllPlaybackState(self, state:AudioPlaybackAction):
        for pool in self.audioGroups:
            # print(state, pool)
            if SoundType.isMasterVolume(self.audioGroups, pool): continue
            # stopping SFX
            stopSFXPool = True if state == AudioPlaybackAction.STOP else False
            if SoundType.isSoundEffect(self.audioGroups, pool) and len(self.audioPool.get(pool)) != 0 and stopSFXPool:
                soundEffectPool:list[SoundEffect] = self.audioPool.get(pool)
                for sound in soundEffectPool:
                    sound.stop()
                rich.print(f'[AudioManager] [green b]Playback All States: [/green b]<{pool}> [red b]{state}[/red b]')
                continue
            elif SoundType.isSoundEffect(self.audioGroups, pool) and stopSFXPool:
                rich.print(f'[AudioManager] [green b]Playback All States: [/green b]<{pool}> [yellow b]Empty SoundEffect Pool[/yellow b]')
                continue
            elif SoundType.isSoundEffect(self.audioGroups, pool) and state in (AudioPlaybackAction.PAUSE, AudioPlaybackAction.PLAY):
                continue
            # else if it's AudioMedia
            audioMediaPool:list[AudioMedia] = self.audioPool.get(pool)
            stateColor = 'b'
            for audio in audioMediaPool:
                #if it's not even loaded with audio, skip
                if not MediaLoaded.contains(audio.mediaStatus()): continue
                match state:
                    case AudioPlaybackAction.PLAY:
                        stateColor = 'cyan b'
                        if audio.playbackState() == PlaybackStatus.PLAYING.value: continue
                    case AudioPlaybackAction.PAUSE:
                        stateColor = 'yellow b'
                        if audio.playbackState() == PlaybackStatus.PAUSED.value: continue
                    case AudioPlaybackAction.STOP:
                        stateColor = 'red b'
                        if audio.playbackState() == PlaybackStatus.STOPPED.value: continue
                # Control the states now
                self._audioMediaControlState(pool, audioMediaPool.index(audio), state)
                # rich.print(f'[AudioManager] Playback State: <{pool}> [{stateColor}]{state}[/{stateColor}]: <{audio}>')
            if not SoundType.isMasterVolume(self.audioGroups, pool) and not SoundType.isSoundEffect(self.audioGroups, pool):
                rich.print(f"[AudioManager] [green b]Playback All States: [/green b]<{pool}> [{stateColor}]{state}[/{stateColor}] [green b]OK")
class SoundEffect(QSoundEffect):
    def __init__(self, file:str, device:QAudioDevice):
        super().__init__()
        self.name = os.path.basename(file)
        self.setAudioDevice(device)
        self.setSource(QUrl.fromLocalFile(file))
    def __repr__(self) -> str:
        return f"{self.name}{':Looped' if self.loopCount() > 1 else ''}"
class AudioMedia(QMediaPlayer):
    def __init__(self, count, device:QAudioDevice):
        super().__init__()
        self.name = count
        # self.keepLoaded = False
        self.device = QAudioOutput(device)
        self.setAudioOutput(self.device)
        # self.mediaStatusChanged.connect(self._clearMedia)
    
    # # Might need to reconsider, and remove this "clearMedia Functionality as we already have an Unload Func"
    # def _clearMedia(self):
    #     # is it EndOfMedia?
    #     # do we want to keep it loaded?
    #     if self.mediaStatus() != QMediaPlayer.MediaStatus.EndOfMedia and not self.keepLoaded:
    #         return
    #     # clear itself
    #     # self.setLoops(1)
    #     self.setSource(QUrl.fromLocalFile(None))
    #     # print({self.name}, 'died')
    
    def getStatus(self) -> tuple:
        src = self.source().toString()
        mediastat = str(self.mediaStatus()).split('.')[1]
        loopstat = f'Looped' if self.loops() > 1 else ''
        playstat = str(self.playbackState()).split('.')[1]
        playrate = round(self.playbackRate(),2)
        return self.name, src, mediastat, loopstat, playstat, playrate
    
    def __repr__(self) -> str:
        # BufferingMedia == Media is being played.
        # EndOfMedia == Media has finished playing. Still indexed.
        name, src, mediastat, loopstat, playstat, playrate = self.getStatus()
        return f"{name}:<{src}>:({mediastat}_{loopstat}{playstat})@[{playrate}x]"
