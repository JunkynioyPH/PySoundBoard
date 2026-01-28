from AudioSystem_PyQt6 import *
from PyQt6.QtMultimedia import QMediaDevices
import xpfpath
from PyQt6.QtWidgets import QApplication

APP = QApplication([])
device = [QMediaDevices.audioOutputs()[2],QMediaDevices.defaultAudioOutput()]
AudioSystem = AudioManager(device[1 ],
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

GenerateSoundIndex('./SoundFiles')
# print('\n AUDIO', AudioSystem.audioIndex[SoundType.AUDIO_MEDIA], '\n'*2)
# print('\n SOUND', AudioSystem.audioIndex[SoundType.SOUND_EFFECT])
AudioSystem.status()
# print("\nGroup Types", AudioSystem.audioGroups)

# print('setDevice')
# AudioSystem.setDevice(QMediaDevices.defaultAudioOutput())
print('mediaControls')
AudioSystem.resumeAll()
AudioSystem.pauseAll()
AudioSystem.stopAll()
# AudioSystem.test('A Maiden Fights')
# AudioSystem.setDevice(QMediaDevices.defaultAudioOutput(),True)
# print('\nAudioPools',AudioSystem.audioPool)
print('\n SETTINGS',AudioSystem.settings)

# AudioSystem.setVolume('master', 2)
# AudioSystem.setVolume('ambient', 30)
# AudioSystem.setVolume('music', 7)
# # AudioSystem.setVolume('music', AudioSystem.settings.get('volume')['master'])
# AudioSystem.setVolume('sfx.name', 15)
# AudioSystem.setVolume('sfxMaster', 6)
print('\n SETTINGS',AudioSystem.settings['volume'])
print(AudioSystem.audioMediaPos('music',2))
print(AudioSystem.audioMediaPos('ambient',0,True))
# AudioSystem.removeIndex(SoundType.AUDIO_MEDIA,'banger')
# AudioSystem.removeIndex(SoundType.AUDIO_MEDIA,'banger')
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
AudioSystem.loadAudioMedia('music','A Maiden Fights')
AudioSystem.loadAudioMedia('music','Duh_Short')
AudioSystem.loadAudioMedia('music','frenchaccordion')
AudioSystem.loadAudioMedia('music','c_mthrone')

# AudioSystem.toggleState('music',AudioPlaybackState.LOOPING)
# AudioSystem.toggleState('music',AudioPlaybackState.MULTIPLE)
AudioSystem.test()
AudioSystem.togglePoolRollOver()
AudioSystem.loadAudioMedia('music','A Maiden Fights')
AudioSystem.loadAudioMedia('music','A Maiden Fights')

AudioSystem.loadAudioMedia('music','A Maiden Fights')
AudioSystem.loadAudioMedia('music','A Maiden Fights')
AudioSystem.loadAudioMedia('music','A Maiden Fights')
AudioSystem.status()

APP.exec()