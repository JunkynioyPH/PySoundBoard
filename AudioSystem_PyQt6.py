import PyQt6.QtMultimedia as QtM # Perhaps a new Backend..?
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
class AudioSystem():
    """AudioSystem wrapping PyQt*.QtMultimedia. To Pre_Initialize, just Define the data in the class itself. e.g. AudioSystem(device=str|None, frequency=int)"""
    def __init__(self, device:str|None=None, frequency:int=48000):
        self.device:str|None = device
        self.frequency:int = frequency
        self.mode:... = ... # SINGLE or MULTI - MODE
        
    def PipelineInfo(self) -> str:
        # print(f"{self.device}@{self.frequency}")
        return f"{self.device}@{self.frequency}"
    
    # more [ def func(): ] here specifically for audio playback.

class AudioPipelineManager:
    def showPipelineList():
        index = 0
        _:AudioSystem
        print('No AudioPipelines to show.') if ActivePipelines == [] else print('\nCurrent AudioPipelines:')
        for _ in ActivePipelines:
            # device/frequency types say [ ANY ] because it's uncertain in this context.
            print(f"{index}: {_} - {_.device}@{_.frequency}")
            index += 1
        else:
            print()
    def createPipeline(device:str|None=None, frequency:int=48000):
        """Load AudioSystem with provided settings or defaults."""
        _:AudioSystem = AudioSystem(device, frequency)
        ActivePipelines.append(_)
        print(f"Created AudioPipeline: {device}@{frequency} - {ActivePipelines[-1]}")
        
    def deletePipeline(index:int=-1):
        """DELETE last created Pipeline or a specified index."""
        print(f"Deleted AudioPipeline: {ActivePipelines[index].device}@{ActivePipelines[index].frequency}")
        ActivePipelines.remove(ActivePipelines[index]) if ActivePipelines != [] else print('No AudioPipelines to delete.')

    def deleteAllPipelines():
        """DELETE ALL AudioPipelines"""
        print('Deleted all active AudioPipelines.') if ActivePipelines != [] else ''
        ActivePipelines.clear() if ActivePipelines != [] else print('AudioPipelines already Clear.')
    
    def PipelineInfo(index:int=0):
        """Display Pipeline Info of INDEX"""
        try:
            pipe:AudioSystem = ActivePipelines[index]
            print(f"AudioPipeline [ {index} ]: {pipe.PipelineInfo()}")
        except:
            print(f'AudioPipeline [ {index} ]: does not exist.')
            
    def bindPipeline(index) -> AudioSystem:
        """RETURN AudioSystem OBJ in ActivePipeline[index]"""
        _:AudioSystem = ActivePipelines[index]
        return _
    
# Standalone, Self test code
if __name__ == "__main__":
    print('Pre Checking...')
    AudioPipelineManager.showPipelineList()           # no Pipeline to show
    AudioPipelineManager.createPipeline()             # create new default Pipeline
    AudioPipelineManager.PipelineInfo(0)              # get info of Pipeline 0
    AudioPipelineManager.PipelineInfo(1)              # get info of Pipeline 1, fails
    AudioPipelineManager.createPipeline('test',44100) # create second Pipeline
    AudioPipelineManager.showPipelineList()           # show list of Pipelines
    AudioPipelineManager.PipelineInfo(1)              # get info of Pipeline 1
    AudioPipelineManager.deletePipeline()             # delete index 0 Pipeline or Pipeline index
    AudioPipelineManager.showPipelineList()           # show list
    AudioPipelineManager.deletePipeline()             # delete index 0 Pipeline or Pipeline index
    AudioPipelineManager.deleteAllPipelines()         # nothing to delete
    AudioPipelineManager.createPipeline()
    AudioPipelineManager.createPipeline()             ### Create 3 Pipelines
    AudioPipelineManager.createPipeline()
    AudioPipelineManager.deleteAllPipelines()         # Delete all Pipelines
    AudioPipelineManager.showPipelineList()
    
    ## Create AudioPipeline and perform Function Tests
    print('\n'+'Practical Testing...')
    AudioPipelineManager.createPipeline()     # Create Default Pipeline
    
    # bind name 'Master' to Pipeline 0
    Master = AudioPipelineManager.bindPipeline(0)
    print(Master.PipelineInfo())
    
