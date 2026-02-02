from os import environ
environ["QT_FFMPEG_LOG_LEVEL"] = "fatal"
environ["QT_LOGGING_RULES"] = "*.debug=false;qt.multimedia.*=false"
from AudioSystem_PyQt6 import *
from PyQt6.QtMultimedia import QMediaDevices
import xpfpath
from PyQt6.QtWidgets import QApplication

APP = QApplication([])
device = [QMediaDevices.audioOutputs()[2],QMediaDevices.defaultAudioOutput()]
AudioSystem = AudioManager(device[0],
                            {'master':SoundType.MASTER_VOLUME,
                            'music':SoundType.AUDIO_MEDIA,
                            'ambient':SoundType.AUDIO_MEDIA,
                            'sfxMaster':SoundType.MASTER_VOLUME,
                            'sfx.name':SoundType.SOUND_EFFECT})

def GenerateSoundIndex(path) -> dict:
    SubFoldersIndex:list[os.DirEntry] = []
    rich.print(f'[yellow][PySoundboard] Scanning [{path}][/yellow]')
    RootFolderContents = os.scandir(path)
    for File in RootFolderContents:
        AudioSystem.addIndex(SoundType.AUDIO_MEDIA,f'{xpfpath.xpfp(File.path)}') if File.is_file() else SubFoldersIndex.append(File.path)
    # Scan Subfolders
    for Folder in SubFoldersIndex:
        rich.print(f'[blue][PySoundboard] Scanning [{Folder}][/blue]')
        SubFolderContents = os.scandir(Folder)
        for File in SubFolderContents:
            AudioSystem.addIndex(SoundType.AUDIO_MEDIA,f'{xpfpath.xpfp(File.path)}') if File.is_file() else SubFoldersIndex.append(File.path)
    # idk but i did anyways
    del RootFolderContents, SubFoldersIndex
    return 0

# GenerateSoundIndex('./SoundFiles')
AudioSystem.addIndex(SoundType.SOUND_EFFECT,'./SoundFiles/FNF/Dah_Short.wav')
AudioSystem.addIndex(SoundType.AUDIO_MEDIA,'./SoundFiles/Hexyz/Chaotic Sacrifice.mp3')
AudioSystem.addIndex(SoundType.AUDIO_MEDIA,'./SoundFiles/Hexyz/Khautic Sacrifice.mp3')


# print('\n AUDIO', AudioSystem.audioIndex[SoundType.AUDIO_MEDIA], '\n'*2)
# print('\n SOUND', AudioSystem.audioIndex[SoundType.SOUND_EFFECT])
AudioSystem.status()
# print("\nGroup Types", AudioSystem.audioGroups)

# print('setDevice')
# AudioSystem.setDevice(QMediaDevices.defaultAudioOutput())
print('mediaControls')
AudioSystem.playAll()
AudioSystem.pauseAll()
AudioSystem.stopAll()
# AudioSystem.test('Chaotic Sacrifice')
# AudioSystem.setDevice(QMediaDevices.defaultAudioOutput(),True)
# print('\nAudioPools',AudioSystem.audioPool)
print('\n SETTINGS',AudioSystem.settings)

AudioSystem.setVolume('master', 2)
AudioSystem.setVolume('ambient', 2)
AudioSystem.setVolume('music', 2)
# # AudioSystem.setVolume('music', AudioSystem.settings.get('volume')['master'])
AudioSystem.setVolume('sfx.name', 2)
AudioSystem.setVolume('sfxMaster', 2)
print('\n SETTINGS',AudioSystem.settings['volume'])
print(AudioSystem.audioMediaPos('music',2))
print(AudioSystem.audioMediaPos('ambient',0,True))
# AudioSystem.removeIndex(SoundType.AUDIO_MEDIA,'banger')
# AudioSystem.removeIndex(SoundType.AUDIO_MEDIA,'banger')
AudioSystem.toggleLooping('music')
AudioSystem.toggleLooping('music')
# AudioSystem.toggleState('music',AudioPlaybackState.MULTIPLE) XXXX
# print('\nMultiMode',AudioSystem.multiMode)
# print('\nLoopMode',AudioSystem.loopMode)
AudioSystem.status()
# a, b = AudioSystem.status(cli=False)
# for each in a:
#     print(each)
# print(a)

AudioSystem.loadAudioMedia('music','gojo_floating')
AudioSystem.loadAudioMedia('music','banger')
AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')
AudioSystem.loadAudioMedia('music','Duh_Short')
AudioSystem.loadAudioMedia('music','frenchaccordion')
AudioSystem.loadAudioMedia('music','c_mthrone')

# AudioSystem.toggleState('music',AudioPlaybackState.LOOPING)
# AudioSystem.toggleState('music',AudioPlaybackState.MULTIPLE)
# AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')
# AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')

# AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')
# AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')
# AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')

AudioSystem.togglePoolRollOver('music')
AudioSystem.togglePoolRollOver('music')
AudioSystem.togglePoolRollOver('music')
# print(AudioSystem.rollOverEnabled)

AudioSystem.togglePoolRollOver('ambient')
AudioSystem.togglePoolRollOver('ambient')
AudioSystem.togglePoolRollOver('ambient')
# print(AudioSystem.rollOverEnabled)

AudioSystem.togglePoolRollOver()
# print(AudioSystem.rollOverEnabled)

AudioSystem.togglePoolRollOver('music')
# print(AudioSystem.rollOverEnabled)x
# AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')
# AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')
# AudioSystem.loadAudioMedia('music','Chaotic Sacrifice')
# AudioSystem.test()

AudioSystem.togglePoolRollOver('master')

AudioSystem.loadAudioMedia('ambient','Chaotic Sacrifice',0)
AudioSystem.loadAudioMedia('ambient','Chaotic Sacrifice',5)

# AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
# AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
# AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
# AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
# AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
# AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
# AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
# AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
AudioSystem.togglePoolRollOver('ambient')

AudioSystem.loadAudioMedia('ambient','A Maiden Fights')
AudioSystem.loadAudioMedia('ambient','A Maiden Fights')

# AudioSystem.playAll()
# AudioSystem.pauseAll()
# AudioSystem.stopAll()
AudioSystem.playSlot('music',0)
rich.print(AudioSystem.audioMediaPos('music',0,True))
# AudioSystem.pauseSlot('music',0)
# AudioSystem.stopSlot('music',0)
AudioSystem.addIndex(SoundType.SOUND_EFFECT,'./SoundFiles/Hexyz/Chaotic Sacrifice.mp3')
# AudioSystem.toggleLooping('sfx.name')

AudioSystem.playSoundEffect('sfx.name','Dah_Short')
AudioSystem.playSoundEffect('sfx.name','Chaotic Sacrifice')

# AudioSystem.status()
# AudioSystem.playAll()
# AudioSystem.pauseAll()
# AudioSystem.stopAll()

APP.exec()