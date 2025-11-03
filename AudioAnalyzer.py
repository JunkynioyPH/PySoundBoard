import numpy
from PyQt6.QtCore import *
from PyQt6.QtMultimedia import *
from PyQt6.QtWidgets import *

class AudioAnalyzer(QObject):
    def __init__(self, device:QAudioDevice=None, sampleRate:int=48000, interval:int=30):
        super().__init__()
        self.fft_ready = pyqtSignal(numpy.ndarray)
        
        if device is None:
            device = QMediaDevices.defaultAudioOutput()
        
        self.audioFormat = QAudioFormat()
        self.audioFormat.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        self.audioFormat.setSampleRate(sampleRate)
        self.audioFormat.setChannelCount(2)
        
        self.audioSource = QAudioSource(device, self.audioFormat)
        self.audioIO = self.audioSource.start()
        self.audioIO.readyRead.connect(self._analyzeAudio) # ReadyReadAudio
        
        self.buffer = bytearray()
        self.updateInterval = QTimer(self)
        self.updateInterval.timeout.connect(self._computeFFT) # ComputeFFT
        self.updateInterval.start(30)
        
    
    def _analyzeAudio(self):
        self.buffer += self.audioIO.readAll().data()
        if len(self.buffer) > 4096:
            self.buffer = self.buffer[-4096:]
    
    def _computeFFT(self):
        if len(self.buffer) < 1024:
            return
        data = numpy.frombuffer(self.buffer, dtype=numpy.int16).astype(numpy.float32)
        data /= 32768.0
        fft = numpy.abs(numpy.fft.rfft(data))
        fft = fft / (numpy.max(fft) + 1e-6)
        # idk, emit is not actually a thing for pyqtSignal, but it is for pyqtBoundSignal
        self.fft_ready.emit(fft)
        print('pog')
        
if __name__ == '__main__':
    APP = QApplication([])
    analyze = AudioAnalyzer()
    print((analyze.fft_ready))