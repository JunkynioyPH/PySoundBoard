import PyQt6.QtMultimedia as QtM # Perhaps a new Backend..?
from PyQt6.QtCore import QUrl

import time

##
# List of Functions i have to re-create or imitate from scratch using PyQt6.Multimedia
##
# init()                 INITIALIZE SYSTEM WITH DEFAULT SETTINGS UNLESS SPECIFIED
# quit()                 CLOSE AUDIO SYSTEM, BASICALLY UNLOAD THE ENTIRE SYSTEM
# *.setvolume()          SET AUDIO SOUND VOLUME
# *.get_pos              GET INFO CURRENT POSITION/DURATION OF AUDIO
# *.load()               LOAD SOUND FILE
# *.unload()             UNLOAD SOUND FILE
# *.play(loopstate=0/-1) PLAY LOADED AUDIO FILE, WHETHER TO LOOP OR NOT LOOP
# *.pause()              TEMPORARILY STOP PLAYBACK
# *.unpause()            CONTINUE PLAYBACK
# *.stop()               STOP AND UNLOAD AUDIO FULE
# *.fadeout()            stop() BUT HAS GRADUAL FADE OUT VOLUME TRANSITION
#
##
# SINGLE/MULTI MODE      CREATE FUNCTIONS SEPARATE FOR SINGLE AND MULTI MODE
##

# List of all Lines
ActivePipelines:list = []
class AudioSystem:
    """AudioSystem wrapping PyQt*.QtMultimedia. To Pre_Initialize, just Define the data in the class itself. e.g. AudioSystem(device=str|None, frequency=int)"""
    def __init__(self, device:QtM.QAudioDevice|None=None, frequency:int=48000):
        self.sound = QtM.QSoundEffect() # create sound effect object
        self.device:QtM.QAudioDevice|None = device
        self.frequency:int = frequency
        
        self.volume:int = 100 # default volume
        # self.mode:... = ... # 0 = SINGLE or 1 = MULTI - MODE
        self.sound.setAudioDevice(device) if device is not None else None # set audio device
        
    def info(self) -> str:
        return f"{self.device.description() if self.device is not None else 'None'}@{self.frequency}"
    
    def play(self, soundfile:str, loopstate:int=0):
        """Play SoundFile with LoopState"""
        print(f"Playing SoundFile[{soundfile}] with LoopState[{loopstate}] on {self.device.description()}@{self.frequency}Hz")
        self.sound.setSource(QUrl.fromLocalFile(soundfile)) # set sound file
        self.sound.setLoopCount(0 if loopstate == 1 else 0) # set loop count NOT YET WORKING
        self.sound.setVolume(self.volume/100) # set volume
        self.sound.play() # play sound
                
    # def stop(self):
    #     """Stop SoundFile Playback"""
    #     print(f"Stopping SoundFile on {self.device}@{self.frequency}Hz")
        
    def setVolume(self, volume:int):
        """Set Volume of AudioSystem"""
        print(f"Setting Volume to {volume}% on {self.device.description()}@{self.frequency}Hz")
        self.volume = volume
    
    # def getPos(self) -> int:
    #     ...
            
    # more [ def func(): ] here specifically for audio playback.

class AudioPipelineManager:
    def showPipelineList():
        index = 0
        _:AudioSystem
        print('No AudioPipelines to show.') if ActivePipelines == [] else print('\nCurrent AudioPipelines:')
        for _ in ActivePipelines:
            # device/frequency types say [ ANY ] because it's uncertain in this context.
            print(f"{index}: {_} - {_.device.description() if _.device is not None else 'None'}@{_.frequency}")
            index += 1
        else:
            print()
    def createPipeline(device:QtM.QAudioDevice|None=None, frequency:int=48000):
        """Load AudioSystem with provided settings or defaults."""
        _:AudioSystem = AudioSystem(device, frequency)
        ActivePipelines.append(_)
        print(f"Created AudioPipeline: {device.description() if device is not None else 'None'}@{frequency} - {ActivePipelines[-1]}")
        
    def deletePipeline(index:int=-1):
        """DELETE last created Pipeline or a specified index."""
        print(f"Deleted AudioPipeline: {ActivePipelines[index].info()}")
        ActivePipelines.remove(ActivePipelines[index]) if ActivePipelines != [] else print('No AudioPipelines to delete.')

    def deleteAllPipelines():
        """DELETE ALL AudioPipelines"""
        print('Deleted all active AudioPipelines.') if ActivePipelines != [] else ''
        ActivePipelines.clear() if ActivePipelines != [] else print('AudioPipelines already Clear.')
    
    def pipelineInfo(index:int=0):
        """Display Pipeline Info of INDEX"""
        try:
            pipe:AudioSystem = ActivePipelines[index]
            print(f"AudioPipeline [ {index} ]: {pipe.info()}")
        except:
            print(f'AudioPipeline [ {index} ]: does not exist.')
            
    def bindPipeline(index) -> AudioSystem:
        """RETURN AudioSystem OBJ from ActivePipeline[index]"""
        _:AudioSystem = ActivePipelines[index]
        return _
    
# Standalone, Self test code
if __name__ == "__main__":
    print('Pre Checking...')
    from PyQt6.QtWidgets import QApplication
    import sys
    from PyQt6.QtWidgets import QMainWindow as MainWindow
    APP = QApplication([])
    MainFrame = MainWindow()
    
    AudioPipelineManager.showPipelineList()           # no Pipeline to show
    AudioPipelineManager.createPipeline()             # create new default Pipeline
    AudioPipelineManager.pipelineInfo(0)              # get info of Pipeline 0
    AudioPipelineManager.pipelineInfo(1)              # get info of Pipeline 1, fails
    AudioPipelineManager.createPipeline(QtM.QMediaDevices.audioOutputs()[0],48000) # create second Pipeline
    AudioPipelineManager.showPipelineList()           # show list of Pipelines
    AudioPipelineManager.pipelineInfo(1)              # get info of Pipeline 1
    AudioPipelineManager.deletePipeline()             # delete index -1 Pipeline or Pipeline index
    AudioPipelineManager.showPipelineList()           # show list
    AudioPipelineManager.deletePipeline()             # delete index -1 Pipeline or Pipeline index
    AudioPipelineManager.deleteAllPipelines()         # nothing to delete
    AudioPipelineManager.createPipeline(QtM.QMediaDevices.audioOutputs()[1])
    AudioPipelineManager.createPipeline(QtM.QMediaDevices.audioOutputs()[2])             ### Create 3 Pipelines
    AudioPipelineManager.createPipeline(QtM.QMediaDevices.audioOutputs()[3])
    AudioPipelineManager.deleteAllPipelines()         # Delete all Pipelines
    AudioPipelineManager.showPipelineList()
    
    ## Create AudioPipeline and perform Function Tests
    print('\n'+'Practical Testing...')
    AudioPipelineManager.createPipeline(device=QtM.QMediaDevices.audioOutputs()[6])     # Create Default Pipeline
    
    # bind name 'Master' to Pipeline 0
    # this is such a round about way of doing it but a lot of the code relies on this list.
    Master = AudioPipelineManager.bindPipeline(0)
    print(Master.info())
    # Master.play('startup.wav', loopstate=1)  # Play test.wav with LoopState 1
    Master.setVolume(14)
    Master.play('./startup.wav', loopstate=1)
    
    MainFrame.show()
    sys.exit(APP.exec())  # Start the Application Event Loop
