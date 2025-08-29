from PyQt6.QtMultimedia import *
from PyQt6.QtCore import QUrl, QTimer
from xpfpath import xpfp
import time, os

# main
class AudioManager():
    def __init__(self, device:QAudioDevice, audioVolume:int=14, soundVolume:int=14, musicPoolSize:int=8):
        """The Main Class which holds everything about the Audio System"""
        print(f"\nSupported MIME Types [QSoundEffect]:\n{QSoundEffect.supportedMimeTypes()}\n\nDetected AudioOutputs:\n{[Device.description() for Device in QMediaDevices.audioOutputs()]}\n")
        print(f'Using Device: {device.description() if device is not None else 'System Default'}\n')
        
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
        """Prints out the current Status of AudioManager"""
        status:str = f"...Index..:\n   Audio: {self.audioIndex['audio']}\n   Sound: {self.audioIndex['sound']}\n\nAudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}"
        if cli:
            print('++ [AudioManager] ++')
            print(status)
            print('++ -------------- ++')
        else:
            return f'AudioPool.:\n   Audio:\n{self.audioPool['audio']}\n\n   Sound:\n{self.audioPool['sound']}'
        
    def setVolume(self, type:str, vol:int):
        # Check if type exist
        if type.lower() not in ('audio','sound'):
            return print("*Unknown Type*")
        
        # update AudioManager Setting
        self.settings['volume'][type.lower()] = vol
        # self.stopAll('sound') if type.lower() == 'sound' else self.pauseAll('audio')
        for each in self.audioPool[type.lower()]:
            if type.lower() == 'sound':
                each.setVolume(self.settings['volume'][type.lower()]/100)
            else:
                each.device.setVolume(self.settings['volume'][type.lower()]/100)
            
    def setDevice(self, device:QAudioDevice):
        self.stopAll('sound')
        self.stopAll('audio')
        self.settings['device'] = device
        for each in self.audioPool['audio']:
            each.device.setDevice(self.settings['device'])
        
    def audioMediaPos(self, index:int):
        item = self.audioPool['audio'][index]
        dur, pos = round(item.duration()/1000,2), round(item.position()/1000,2)
        return f"{index}: {f"{pos} s" if pos < 60 else f"{round(pos/60,2)} min"} / {f'{dur} s' if dur < 60 else f'{round(dur/60,2)} min'}"
        
    def load(self, type:str, path:str):
        audioName:str = os.path.splitext(os.path.basename(path))[0]
        print(f"[AudioManager] Load: ({type}) '{audioName}' <{path}> ", end='')
        
        ## Normalise path to have ' ./ , .\\ ' prefix
        ## In windows, this check will fail and duplicate " .\\ "
        ## However, " .\\.\\ " will still point to "Current Directory"
        ## I Should probably use "os.path" stuff for this instead of xpfp() shit thing i made
        path = path if xpfp('./') in path else xpfp(f'./{path}')
        
        # Check if type exist
        if type.lower() not in ('audio','sound'):
            return print("*Unknown Type*")
        # Check if key exist in dict, say it's a duplicate if it is
        if  self.audioIndex[type.lower()].get(audioName):
            return print(f'*Duplicate*')
        
        # else, make key
        if type.lower() == 'audio':
            self.audioIndex['audio'][audioName] = path
            print(f"*Loaded*")
        else:
            self.audioIndex['sound'][audioName] = path
            print(f"*Loaded*")
                
    def unload(self, type:str, item:str):
        print(f"[AudioManager] Unload: ({type}) <{item}> ", end='')
        # Check if type exist
        if type.lower() not in ('audio','sound'):
            return print("*Unknown Type*")
        # If it exists, ever. if not reply already unloaded
        if not self.audioIndex.get(type.lower()) and not self.audioIndex[type.lower()].get(item):
            return print(f"*Already Unloaded*")

        # else, unload
        if type.lower() == 'audio':
            self.audioIndex['audio'].pop(item)
            print(f"*Unloaded*")
        else:
            self.audioIndex['sound'].pop(item)
            print(f"*Unloaded*")
    
    def toggleState(self, type:str, mode:str):
        print(f"[AudioManager] ToggleState: ({type}) '{mode}' ", end='')
        if type.lower() not in ('audio','sound'):
            return print('*Unknown Type*')
        if mode.lower() not in ('multi','loop'):
            return print('*Unknown Mode*')
        
        if mode.lower() == 'multi':
            self.multiMode[type.lower()] = True if self.multiMode[type.lower()] != True else False
            print(f"{self.multiMode[type.lower()]} ", end='')
        else:
            self.loopMode[type.lower()] = True if self.loopMode[type.lower()] != True else False
            print(f"{self.loopMode[type.lower()]} ", end='')
        print("*Done*")
    
    def play(self, type:str, item:str):
        print(f"[AudioManager] Play: ({type}) <{item}> ", end='')
        
        looping = int(((2**32) / 2) - 1) if self.loopMode[type.lower()] else 1
        
        # Check if type exist in the list
        if type.lower() not in ('audio','sound'):
            return print("*Unknown Type*")
        # Check if the audio actually exist in audioIndex
        audioName = self.audioIndex[type.lower()].get(item)
        if not audioName:
            return print(f'*Not Found*')
        
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
            
        def _playAudioMedia(poolItem:AudioMedia, Source:QUrl, volume:int, loops:int):
            poolItem.setSource(Source)
            poolItem.setLoops(loops)
            poolItem.device.setVolume(volume)
            poolItem.play()
            
        if type.lower() == 'audio':
            if self.multiMode['audio'] == True:
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
                    return
                else:
                    if self.rollingPoolIndex == len(self.audioPool['audio']):
                        self.rollingPoolIndex = 0
                    print(f"<reusing> {self.audioPool['audio'][self.rollingPoolIndex]} ", end='')
                    rollingIndex = self.audioPool['audio'][self.rollingPoolIndex]
                    _playAudioMedia(rollingIndex, QUrl.fromLocalFile(self.audioIndex['audio'].get(item)), self.settings['volume']['audio']/100, looping)
                    self.rollingPoolIndex += 1
            else:
                poolItem = self.audioPool['audio'][0]
                _playAudioMedia(poolItem, QUrl.fromLocalFile(self.audioIndex['audio'].get(item)), self.settings['volume']['audio']/100, looping)
            print('*Done*')
        else:
            # create new instance of SoundEffect
            _ = SoundEffect(self.audioIndex['sound'].get(item), self.settings['device'], self.settings['volume'], looping)

            # add to pool and delete instance once audio finishes
            self.audioPool['sound'].append(_)
            _.playingChanged.connect(lambda: _vanish(_))
            print("*Done*")
    
    def stopAll(self, type:str):
        if type.lower() not in ('audio','sound'):
            return print("*Unknown Type*")
        if type.lower() == 'sound':
            # Brute Force method of stopping all SoundEffect. since if .stop is called, .playingChanged triggers which removes itself
            while self.audioPool.get('sound') != []:
                print(f'[AudioManager] Stop: {self.audioPool.get('sound')[0]}')
                
                # these 3 lines makes no sense to me but it works
                self.audioPool.get('sound')[0].play() if self.audioPool.get('sound')[0].keptAlive == True else ''
                self.audioPool.get('sound')[0].keptAlive = False
                self.audioPool.get('sound')[0].stop()

        else:
            # Loop through all items in preloaded pool and stop them + clear Media
            for each in self.audioPool.get('audio'):
                if each.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia:
                    continue
                print(f'[AudioManager] Stop: {each}')
                each.stop()
                each.setSource(QUrl(QUrl.fromLocalFile(None)))
                
    def resumeAll(self, type:str):
        if type.lower() not in ('audio','sound'):
            return print("*Unknown Type*")
        # Brute Force method of stopping all SoundEffect. since if .stop iscalled, .playingChanged triggers which removes itself
        if type.lower() == 'sound':
            for each in self.audioPool['sound']:
                print(f'[AudioManager] Replay:{each}')
                # play it, which will trigger .playingChanged, but... Paused is TRUE so it returns! _vanish() not triggered
                # this line makes no sense to me why i needa check keptAlive state but it works
                each.play() if each.keptAlive == True else ''
                # THEN unpause variable
                each.keptAlive = False
                
        else:
            for each in self.audioPool.get('audio'):
                if each.playbackState() != QMediaPlayer.PlaybackState.PausedState:
                    continue
                print(f'[AudioManager] Resume: {each}')
                each.play()
                
    
    def pauseAll(self, type:str):
        if type.lower() not in ('audio','sound'):
            return print("*Unknown Type*")
        if type.lower() == 'sound':
            for each in self.audioPool['sound']:
                print(f'[AudioManager] Halt: {each}')
                each.keptAlive = True
                each.stop()
        else:
            for each in self.audioPool.get('audio'):
                if each.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                    continue
                print(f'[AudioManager] Pause: {each}')
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
