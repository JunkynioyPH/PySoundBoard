from AudioSystem_PyQt6 import *
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QPushButton
    import sys
    from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
    
    APP = QApplication([])
    class FuncButton(QPushButton):
        def __init__(self, Name:str, Method):
            super().__init__()
            self.setText(Name)
            self.setStyleSheet("text-align: left; padding: 5%; margin: 0%;")
            self.setFixedWidth(125)
            # self.Method = Method # keep alive
            self.clicked.connect(Method)
            
    #this is for reference later
    #this is to keep alive what sound is per button
    class SoundButton(FuncButton):
        def __init__(self, Type:str, Name:str, Method):
            self.name:str = Name
            self.type = Type
            self.playAudio = Method
            super().__init__(self.name, self.play)
        def play(self):
            self.playAudio(f'{self.type}',f'{self.name}')

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            Canvas = QWidget()

            VBox = QVBoxLayout()
            self.setCentralWidget(Canvas)
            Canvas.setLayout(VBox)
            
            self.device = QMediaDevices.audioOutputs()[3] # simulate loading prefered audioDevice
            self.sound = AudioManager(self.device,14) # init AudioSystem
            
            self.sound.load('sound','startup.wav')     # load sound
            self.sound.load('audio','startup.wav')     # load audio
            self.sound.load('vibration','startup.wav') # load unknown
            
            self.sound.unload('sound','startup')  # unload
            self.sound.unload('sound','startup')  # already unloaded
            self.sound.unload('sounds','startup') # invalid type
            
            self.sound.unload('audio','startup')   # unload
            self.sound.unload('audio','startup')   # already unloaded
            self.sound.unload('audios','startup')  # invalid type
            
            self.sound.load('sound','./startup.wav')     # load sound ./
            self.sound.load('sound','./SoundFiles/Question.wav')     # load sound ./
            self.sound.load('audio','./startup.wav')     # load audio ./
            
            self.sound.load('audio','./SoundFiles/bonk.mp3') # load sound from nested folders
            self.sound.load('audio','SoundFiles/bonk.mp3')
            
            ## monitor sound list
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.sound.status)
            self.timer.start(500)
            
            # learned lambda
            for each in self.sound.audioIndex['sound']:    
                print(each) 
                VBox.addWidget(SoundButton(f'sound', f'{each}', self.sound.play))
            for each in self.sound.audioIndex['sound']:    
                print(each) 
                VBox.addWidget(SoundButton(f'audio', f'{each}', self.sound.play))
    
            self.sound.toggleState('sound','multi')
            self.sound.toggleState('audio','multi')
            self.sound.toggleState('sound','multi')
            self.sound.toggleState('audio','multi')
            
            self.sound.toggleState('sound','loop')
            self.sound.toggleState('audio','loop')
            self.sound.toggleState('sound','loop')
            self.sound.toggleState('audio','loop')
            
    MainFrame = MainWindow()
    MainFrame.show()
    sys.exit(APP.exec())  # Start the Application Event Loop