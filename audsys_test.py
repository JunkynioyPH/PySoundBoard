from AudioSystem_PyQt6 import *
from PyQt6.QtMultimedia import QMediaDevices
import xpfpath
from PyQt6.QtWidgets import QApplication

APP = QApplication([])
AudioSystem = AudioManager(QMediaDevices.defaultAudioOutput(),
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
        AudioSystem.addIndex('audio',f'{xpfpath.xpfp(File.path)}') if File.is_file() else SubFoldersIndex.append(File.path)
    # Scan Subfolders
    for Folder in SubFoldersIndex:
        rich.print(f'[blue][PySoundboard] Scanning [{Folder}][/blue]')
        SubFolderContents = os.scandir(Folder)
        for File in SubFolderContents:
            AudioSystem.addIndex('audio',f'{xpfpath.xpfp(File.path)}') if File.is_file() else SubFoldersIndex.append(File.path)
    # idk but i did anyways
    del RootFolderContents, SubFoldersIndex
    return 0

GenerateSoundIndex('./SoundFiles')
print('\n AUDIO', AudioSystem.audioIndex['audio'], '\n'*2)
print('\n SOUND', AudioSystem.audioIndex['sound'])
print('\n SETTINGS',AudioSystem.settings)
print("\nGroup Types", AudioSystem.audioGroups)
print('\nAudioPools',AudioSystem.audioPool)
print('\nMultiMode',AudioSystem.multiMode)
print('\nLoopMode',AudioSystem.loopMode)

print('setDevice')
AudioSystem.setDevice(QMediaDevices.defaultAudioOutput())
print('mediaControls')
AudioSystem.resumeAll()
AudioSystem.pauseAll()
AudioSystem.stopAll()

print('Test playback of', SoundType.SOUND_EFFECT,'and stopAll for', SoundType.SOUND_EFFECT)
AudioSystem.test('vineboom')

print('attempt to change audio when SoundEffect is playing a sound.\nneeds to be tested @ Runtime APP.exec()')
AudioSystem.setDevice(QMediaDevices.defaultAudioOutput())

APP.exec()