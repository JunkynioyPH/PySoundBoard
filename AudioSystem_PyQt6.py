from PyQt6.QtMultimedia import *
from PyQt6.QtCore import QUrl, QTimer
from xpfpath import xpfp
import time, os, rich
from rich import pretty
pretty.install()


# main
class AudioManager():
    def __init__(self, device:QAudioDevice, audioVolume:int=14, soundVolume:int=14, musicPoolSize:int=8):
        """The Main Class which holds everything about the Audio System"""
        rich.print(f"\nSupported MIME Types [QSoundEffect]:\n{QSoundEffect.supportedMimeTypes()}\n\nDetected AudioOutputs:\n{[Device.description() for Device in QMediaDevices.audioOutputs()]}\n")
        rich.print(f'Using Device: {device.description() if device is not None else 'System Default'}\n')
        
        self.settings:dict[str, QAudioDevice|dict[str, int]] = {"device":device,"volume":{'audio':audioVolume,'sound':soundVolume}}
        
        self.multiMode:dict[str, bool] = {'audio':False, 'sound':False}
        self.loopMode:dict[str, bool] = {'audio':False, 'sound':False}
        
        self.rollingPoolIndex:int = 0
        self.audioPool:dict[str, list[SoundEffect|AudioMedia]] = {'audio':[],'sound':[]}
        self.audioIndex:dict[str, dict[str, str]] = {'audio':{},'sound':{}}
        
        self._initAudioMediaPool(musicPoolSize)
        
    def _initAudioMediaPool(self, poolCount):
        self.audioPool['audio'] = []
        for count in range(0,poolCount):
            self.audioPool['audio'].append(AudioMedia(count, self.settings['device']))
        pass
             
    def status(self, cli:bool=True) -> None|str:
        """rich.prints out the current Status of AudioManager"""
        status:str = f"...Index..:\n   Audio: {self.audioIndex['audio']}\n   Sound: {self.audioIndex['sound']}\n\nAudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}"
        if cli:
            rich.print('++ [AudioManager] ++')
            rich.print(status)
            rich.print('++ -------------- ++')
        else:
            return f'AudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}'
        
    def setVolume(self, type:str, vol:int):
        # Check if type exist
        if type.lower() not in ('audio','sound'):
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        
        # update AudioManager Setting
        self.settings['volume'][type.lower()] = vol
        # self.stopAll('sound') if type.lower() == 'sound' else self.pauseAll('audio')
        for each in self.audioPool[type.lower()]:
            if type.lower() == 'sound':
                each.setVolume(self.settings['volume'][type.lower()]/100)
            else:
                each.device.setVolume(self.settings['volume'][type.lower()]/100)
            
    def setDevice(self, device:QAudioDevice, stopAll:bool=False):
        self.stopAll('sound')
        self.stopAll('audio') if stopAll else self.pauseAll('audio')
        self.settings['device'] = device
        for each in self.audioPool['audio']:
            each.device.setDevice(self.settings['device'])
        '' if stopAll else self.resumeAll('audio')
        
    def audioMediaPos(self, index:int):
        item = self.audioPool['audio'][index]
        dur, pos = round(item.duration()/1000,2), round(item.position()/1000,2)
        return f"{index}: {f"{pos} s" if pos < 60 else f"{round(pos/60,2)} min"} / {f'{dur} s' if dur < 60 else f'{round(dur/60,2)} min'}"
        
    def load(self, type:str, path:str):
        audioName:str = os.path.splitext(os.path.basename(path))[0]
        rich.print(f"[AudioManager] [green]Load:[/green] ({type}) '{audioName}' [magenta b]<{path}>[/magenta b] ", end='')
        
        ## Normalise path to have ' ./ , .\\ ' prefix
        ## In windows, this check will fail and duplicate " .\\ "
        ## However, " .\\.\\ " will still point to "Current Directory"
        ## I Should probably use "os.path" stuff for this instead of xpfp() shit thing i made
        path = path if xpfp('./') in path else xpfp(f'./{path}')
        
        # Check if type exist
        if type.lower() not in ('audio','sound'):
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        # Check if key exist in dict, say it's a duplicate if it is, and append disriminator
        if  self.audioIndex[type.lower()].get(audioName):
            audioName = f"{len(self.audioIndex['audio'])^len(audioName)}_{audioName}"
            rich.print(f'as [blue]<{audioName}>[/blue] ', end='')
        
        # else, make key
        if type.lower() == 'audio':
            self.audioIndex['audio'][audioName] = path
            rich.print(f"[green b]*Loaded*[/green b]")
        else:
            self.audioIndex['sound'][audioName] = path
            rich.print(f"[green b]*Loaded*[/green b]")
                
    def unload(self, type:str, item:str):
        rich.print(f"[AudioManager] [red]Unload:[/red] ({type}) [magenta b]<{item}>[/magenta b] ", end='')
        # Check if type exist
        if type.lower() not in ('audio','sound'):
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        # If it exists, ever. if not reply already unloaded
        if not self.audioIndex.get(type.lower()) and not self.audioIndex[type.lower()].get(item):
            return rich.print(f"[red b]*Already Unloaded*[/red b]")

        # else, unload
        if type.lower() == 'audio':
            self.audioIndex['audio'].pop(item)
            rich.print(f"[red b]*Unloaded*[/red b]")
        else:
            self.audioIndex['sound'].pop(item)
            rich.print(f"[red b]*Unloaded*[/red b]")
    
    def toggleState(self, type:str, mode:str):
        rich.print(f"[AudioManager] ToggleState: ({type}) '{mode}' ", end='')
        if type.lower() not in ('audio','sound'):
            return rich.print('[yellow b]*Unknown Type*[/yellow b]')
        if mode.lower() not in ('multi','loop'):
            return rich.print('*Unknown Mode*')
        
        if mode.lower() == 'multi':
            self.multiMode[type.lower()] = True if self.multiMode[type.lower()] != True else False
            rich.print(f"{self.multiMode[type.lower()]} ", end='')
        else:
            self.loopMode[type.lower()] = True if self.loopMode[type.lower()] != True else False
            rich.print(f"{self.loopMode[type.lower()]} ", end='')
        rich.print("*Done*")
    
    def play(self, type:str, item:str):
        rich.print(f"[AudioManager] [blue b]Play:[/blue b] ({type}) [magenta b]<{item}>[/magenta b] ", end='')
        
        looping = int(((2**32) / 2) - 1) if self.loopMode[type.lower()] else 1
        
        # Check if type exist in the list
        if type.lower() not in ('audio','sound'):
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        # Check if the audio actually exist in audioIndex
        audioName = self.audioIndex[type.lower()].get(item)
        if not audioName:
            return rich.print(f'[red b]*Not Found*[/red b]')
        
        # if it's not empty, something is already playing, remove it and proceed
        # else add to pool
        if self.audioPool['sound'] != [] and self.multiMode['sound'] == False:
            self.audioPool['sound'][0].stop()
        
        # clean up after sound is done playing
        def _vanish(sound:SoundEffect):
            if sound.keptAlive:
                return
            pool = self.audioPool['sound']
            pool.remove(sound)
        
        # shorten
        def _playAudioMedia(poolItem:AudioMedia, Source:QUrl, volume:int, loops:int):
            poolItem.setSource(Source)
            poolItem.setLoops(loops)
            poolItem.device.setVolume(volume)
            poolItem.play()
            
        if type.lower() == 'audio':
            if self.multiMode['audio']: # if true'
                for poolItem in self.audioPool['audio']:
                    
                    # Skip if it's not EndOfMedia | NoMedia
                    if poolItem.mediaStatus() not in (QMediaPlayer.MediaStatus.EndOfMedia, QMediaPlayer.MediaStatus.NoMedia):
                        # != EndOfMedia|NoMedia
                        # In the event that all of the pool are in use, this will
                        # actually finish the rest of iteration and
                        # trigger the 'else' statement below.
                        continue
                    
                    #
                    # parameters:
                    # QUrl.fromLocalFile(self.audioIndex['audio'].get(item))
                    # self.settings['volume']['audio']/100
                    #
                    # if it's EndOfMedia | NoMedia AND StoppedState
                    _playAudioMedia(poolItem, QUrl.fromLocalFile(self.audioIndex['audio'].get(item)), self.settings['volume']['audio']/100, looping)
                    rich.print('*Done*')
                    return
                else:
                    if self.rollingPoolIndex == len(self.audioPool['audio']):
                        self.rollingPoolIndex = 0
                    rich.print(f"[yellow b]<reusing> {self.audioPool['audio'][self.rollingPoolIndex]}[/yellow b] ", end='')
                    rollingIndex = self.audioPool['audio'][self.rollingPoolIndex]
                    _playAudioMedia(rollingIndex, QUrl.fromLocalFile(self.audioIndex['audio'].get(item)), self.settings['volume']['audio']/100, looping)
                    self.rollingPoolIndex += 1
            else:
                poolItem = self.audioPool['audio'][0]
                _playAudioMedia(poolItem, QUrl.fromLocalFile(self.audioIndex['audio'].get(item)), self.settings['volume']['audio']/100, looping)
            rich.print('*Done*')
        else:
            if self.multiMode['sound']:
                # create new instance of SoundEffect
                _ = SoundEffect(self.audioIndex['sound'].get(item), self.settings['device'], self.settings['volume']['sound'], looping)

                # add to pool and delete instance once audio finishes
                self.audioPool['sound'].append(_)
                _.playingChanged.connect(lambda: _vanish(_))
                rich.print("*Done*")
            else:
                _ = SoundEffect(self.audioIndex['sound'].get(item), self.settings['device'], self.settings['volume']['sound'], looping)
                if self.audioPool['sound'] != []:
                    self.audioPool['sound'][0].stop()
                    self.audioPool['sound'].append(_)
                else:
                    self.audioPool['sound'].append(_)
                _.playingChanged.connect(lambda: _vanish(_))
                rich.print("*Done*")
    
    def stopAll(self, type:str):
        if type.lower() not in ('audio','sound'):
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        if type.lower() == 'sound':
            # Brute Force method of stopping all SoundEffect. since if .stop is called, .playingChanged triggers which removes itself
            while self.audioPool.get('sound') != []:
                rich.print(f'[AudioManager] Stop: {self.audioPool.get('sound')[0]}')
                
                # these 3 lines makes no sense to me but it works
                self.audioPool.get('sound')[0].play() if self.audioPool.get('sound')[0].keptAlive == True else ''
                self.audioPool.get('sound')[0].keptAlive = False
                self.audioPool.get('sound')[0].stop()

        else:
            # Loop through all items in preloaded pool and stop them + clear Media
            for each in self.audioPool.get('audio'):
                if each.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia:
                    continue
                rich.print(f'[AudioManager] [red b]Stop: {each}[/red b]')
                each.stop()
                each.setSource(QUrl.fromLocalFile(None))
                
    def resumeAll(self, type:str):
        if type.lower() not in ('audio','sound'):
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        # Brute Force method of stopping all SoundEffect. since if .stop iscalled, .playingChanged triggers which removes itself
        if type.lower() == 'sound':
            for each in self.audioPool['sound']:
                rich.print(f'[AudioManager] Replay:{each}')
                # play it, which will trigger .playingChanged, but... Paused is TRUE so it returns! _vanish() not triggered
                # this line makes no sense to me why i needa check keptAlive state but it works
                each.play() if each.keptAlive == True else ''
                # THEN unpause variable
                each.keptAlive = False
                
        else:
            for each in self.audioPool.get('audio'):
                if each.playbackState() != QMediaPlayer.PlaybackState.PausedState:
                    continue
                rich.print(f'[AudioManager] [cyan b]Resume: {each}[/cyan b]')
                each.play()
                
    
    def pauseAll(self, type:str):
        if type.lower() not in ('audio','sound'):
            return rich.print("[yellow b]*Unknown Type*[/yellow b]")
        if type.lower() == 'sound':
            for each in self.audioPool['sound']:
                rich.print(f'[AudioManager] Halt: {each}')
                each.keptAlive = True
                each.stop()
        else:
            for each in self.audioPool.get('audio'):
                if each.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                    continue
                rich.print(f'[AudioManager] [yellow b]Pause: {each}[/yellow b]')
                each.pause()
            

class SoundEffect(QSoundEffect):
    def __init__(self, file:str, device:QAudioDevice, volume:int, loops:int):
        super().__init__()
        self.name = os.path.basename(file)
        self.setAudioDevice(device)
        self.setSource(QUrl.fromLocalFile(file))

        self.keptAlive = False
        self.setVolume(volume/100)
        self.setLoopCount(loops)
        self.play()
        
    def __repr__(self) -> str:
        return f"{self.name}{' (looped)' if self.loopCount() > 1 else ''}"

###
#  Plan to add PlaybackRate. maybe slowmo, or fast-mo functions.
###
#  Plan to add a slight delay when playing and unloading Media,
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
        # EndOfMedia == Media has finished playing. Still Loaded.
        return f"{self.name}:<{self.source().toString()}>:({str(self.mediaStatus()).split('.')[1]}_{f'Looped' if self.loops() > 1 else ''}{str(self.playbackState()).split('.')[1]})"
