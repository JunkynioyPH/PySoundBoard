# AudioManager.py

import os
import PyQt6.QtMultimedia as QTM
from PyQt6.QtCore import QUrl

class AudioManager:
    def __init__(self, device: QTM.QAudioDevice, volume: int = 50):
        self.device = device
        self.volume = volume
        self.loaded: dict[str, str] = {}  # name -> file path
        self.pool = {
            "sound": [],  # List[SoundEffectPlayer]
            "music": []   # List[MediaPlayerWrapper]
        }

    def load(self, name: str, path: str):
        full_path = os.path.abspath(path)
        self.loaded[name] = full_path

    def playSound(self, name: str, loop=False):
        path = self.loaded.get(name)
        if not path:
            print(f"[AudioManager] Sound '{name}' not found.")
            return
        player = SoundEffectPlayer(path, self.device, self.volume, loop)
        self.pool["sound"].append(player)
        player.play()
        player.playingChanged.connect(lambda: self._cleanup("sound", player))

    def playMusic(self, name: str, loop=False):
        path = self.loaded.get(name)
        if not path:
            print(f"[AudioManager] Music '{name}' not found.")
            return
        player = MediaPlayerWrapper(path, self.device, self.volume, loop)
        self.pool["music"].append(player)
        player.play()
        player.mediaPlayer.mediaStatusChanged.connect(
            lambda status: self._cleanup("music", player) if status == QTM.QMediaPlayer.MediaStatus.EndOfMedia else None
        )

    def _cleanup(self, pool_name, player):
        try:
            if pool_name == "sound":
                player.playingChanged.disconnect()
                if not player.isPlaying():
                    self.pool[pool_name].remove(player)
            elif pool_name == "music":
                self.pool[pool_name].remove(player)
        except Exception:
            pass

    def cleanup(self):
        for player in self.pool["sound"]:
            try:
                player.stop()
                player.playingChanged.disconnect()
            except Exception:
                pass
        for player in self.pool["music"]:
            try:
                player.stop()
                player.mediaPlayer.mediaStatusChanged.disconnect()
            except Exception:
                pass
        self.pool["sound"].clear()
        self.pool["music"].clear()


class SoundEffectPlayer(QTM.QSoundEffect):
    def __init__(self, file: str, device: QTM.QAudioDevice, volume: int, loop: bool):
        super().__init__()
        self.setSource(QUrl.fromLocalFile(file))
        self.setAudioDevice(device)
        self.setVolume(volume / 100)
        self.setLoopCount(int(((2**32) / 2) - 1) if loop else 1)

    def __repr__(self):
        return f"<SoundEffectPlayer {self.source().toString()} Playing={self.isPlaying()}>"


class MediaPlayerWrapper:
    def __init__(self, file: str, device: QTM.QAudioDevice, volume: int, loop: bool):
        self.mediaPlayer = QTM.QMediaPlayer()
        self.audioOutput = QTM.QAudioOutput(device)
        self.audioOutput.setVolume(volume / 100)
        self.mediaPlayer.setAudioOutput(self.audioOutput)
        self.mediaPlayer.setSource(QUrl.fromLocalFile(file))
        if loop:
            self.mediaPlayer.setLoops(QTM.QMediaPlayer.Loops.Infinite)
        else:
            self.mediaPlayer.setLoops(1)

    def play(self):
        self.mediaPlayer.play()

    def stop(self):
        self.mediaPlayer.stop()

    def __repr__(self):
        return f"<MediaPlayerWrapper {self.mediaPlayer.source().toString()} Playing={self.mediaPlayer.playbackState()}>"
