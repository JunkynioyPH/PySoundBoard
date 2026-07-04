from rich import pretty
pretty.install()
import json, os, sys, rich
# QSize, QUrl
# from PyQt6.QtGui import QPixmap, QRegion # MAYBE ill get to work this at some point lmao
from PyQt6.QtCore import Qt, QTimer, QObject, QEvent, QThread, pyqtSlot, pyqtSignal
from PyQt6.QtMultimedia import QMediaDevices
from PyQt6.QtWidgets import *
# from difflib import get_close_matches
import PySoundboard_Helper_PyQt6 as PSbHelper
APP = QApplication([])
# Initialise Instance of QApp
_ = QMediaDevices.audioOutputs(); del _ # Moving the FFMPEG thing
# Console splash
def splashCli():
    # os.system('cls' if os.name=='nt' else 'clear')
    os.system('title PySoundBoard Backend') if os.name=='nt' else rich.print('\nPySoundBoard Backend')
    rich.print('''

    ██████╗ ██╗   ██╗███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██████╗  ██████╗  █████╗ ██████╗ ██████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
    ██████╔╝ ╚████╔╝ ███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║
    ██╔═══╝   ╚██╔╝  ╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║
    ██║        ██║   ███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
    ╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
                        Written By : @junkynioy - https://github.com/JunkynioyPH        PyQt6 RE: GUI_E.B.
    ''')
def ShowSettings():
    rich.print("[PySoundboard] ", end='')
    for i in Settings:
        rich.print(f"[yellow][{i}:{Settings[i]}][/yellow] ", end='')
    else:
        print()
def UpdateSettings(Variable,Value):
    rich.print(f"[PySoundboard] [green]Update Setting:[/green] <{Variable}> to '{Value}'")
    Settings[Variable] = Value
    with open("Settings.json","w") as UpdateSettings:
        UpdateSettings.write(json.dumps(Settings))
    PSbHelper.InitializeSettings() # Reload Settings
    ShowSettings()
def setAppTheme(bool:bool):
    if not bool:
        import darkmode
        APP.setStyle('Fusion'); APP.setPalette(darkmode.get_slate_blue_dark_palette())
        rich.print('[PySoundboard] Using Built-in Dark Theme')
    else:
        rich.print('[PySoundboard] Using System Theme')
# Show First-Time Execution then turn off pop up
# need to replace
def splashInfo(unseen:bool):
    if unseen:
        rich.print('='*20)
        UpdateSettings("Splash",False)
class updateTimerQueue(QTimer):
    def __init__(self, parent=None, ticks:int|None=None):
        super().__init__(parent)
        self.updateList:list = []
        self.timeout.connect(self.update)
        self.start(ticks) if ticks else self.start(250)
    def update(self):
        for item in self.updateList:
            item()
    def appendToQueue(self, _callable):
        rich.print('[PySoundboard] UpdateTimerQueue: ', end='')
        if not callable(_callable):
            return rich.print(f'[red]Not Callable [/red]{_callable}')
        rich.print(f'[green]Appended [/green]{_callable}')
        self.updateList.append(_callable)
    def popQueueItem(self, index:int):
        self.updateList.pop(index)
class sections:
    class SoundButtons(QGroupBox):
        def __init__(self, title, parent:"MainWindow"=None):
            super().__init__(title, parent)
            self.progenitor = parent
            self.soundButtonsCanvas = QVBoxLayout()
            self.soundButtonsRefreshListButton = FuncButton('Refresh Tab Lists', self.refreshButtons)
            self.refreshButtonDisplayLabel = QLabel('Refreshing Buttons...')
            self.refreshButtonDisplayLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.refreshButtonDisplayLabel.setStyleSheet('font-size: 70px;')
            self.soundButtonsCanvas.addWidget(self.soundButtonsRefreshListButton)
            self.soundButtonsCanvas.addWidget(self.refreshButtonDisplayLabel)
            self.refreshButtonDisplayLabel.setHidden(True)
            # SoundButtonsFilterBar = QHBoxLayout()
            # self.soundButtonsFilterTextBox = QLineEdit()
            # self.soundButtonsFilterTextBox.setPlaceholderText('Filter Search...')
            # SoundButtonsFilterBar.addWidget(self.soundButtonsFilterTextBox)
            # SoundButtonsFilterBar.addWidget(self.soundButtonsRefreshListButton)
            # self.soundButtonsCanvas.addLayout(SoundButtonsFilterBar)
            self._bakeButtonThreadingWrapper()
        class threadedSoundIndexer(QObject):
            soundIndexReady = pyqtSignal(dict)
            @pyqtSlot()
            def _generateSoundIndex(self):
                returnValue = PSbHelper.GenerateSoundIndex(AudioSystem, os.path.join('./SoundFiles'))
                self.soundIndexReady.emit(returnValue)
        class threadedSoundButtonRemover(QObject):
            soundButtonsCleared = pyqtSignal()
            @pyqtSlot()
            def _clearIndex(self):
                AudioMediaIndex = list(AudioSystem.audioIndex.get(PSbHelper.SoundType.AUDIO_MEDIA))
                for indexItem in AudioMediaIndex:
                    AudioSystem.removeIndex(PSbHelper.SoundType.AUDIO_MEDIA, indexItem)
                else:
                    self.soundButtonsCleared.emit()
        def _bakeButtonThreadingWrapper(self):
            ## AI ASSISTED, QTHREAD, IMPLEMENTATION. NOW I KNOW HOW TO THREAD-ish :)
            self.threadingObj = QThread(self)
            self.soundIndexGenerator = self.threadedSoundIndexer()
            self.soundIndexGenerator.moveToThread(self.threadingObj)
            self.threadingObj.started.connect(self.soundIndexGenerator._generateSoundIndex)
            self.soundIndexGenerator.soundIndexReady.connect(self.bakeButtons)
            self.soundIndexGenerator.soundIndexReady.connect(self.threadingObj.quit)
            self.soundIndexGenerator.soundIndexReady.connect(self.soundIndexGenerator.deleteLater)
            # self.threadingObj.finished.connect(self.soundIndexGenerator.deleteLater)
            self.threadingObj.finished.connect(splashCli)
            self.threadingObj.finished.connect(ShowSettings)
            self.threadingObj.start(QThread.Priority.TimeCriticalPriority)
        def _RebakeButtonsThreadingWrapper(self):
            self.threadingObj = QThread(self)
            self.soundIndexClearing = self.threadedSoundButtonRemover()
            self.soundIndexClearing.moveToThread(self.threadingObj)
            self.threadingObj.started.connect(self.soundIndexClearing._clearIndex)
            self.soundIndexClearing.soundButtonsCleared.connect(self.threadingObj.quit)
            self.soundIndexClearing.soundButtonsCleared.connect(self.soundIndexClearing.deleteLater)
            self.soundIndexClearing.soundButtonsCleared.connect(self._bakeButtonThreadingWrapper)
            self.threadingObj.finished.connect(self.soundIndexClearing.deleteLater)
            self.threadingObj.start(QThread.Priority.TimeCriticalPriority)
        def bakeButtons(self, buttonIndex:dict):
            self.buttonTabsCanvas = QTabWidget()
            self.setLayout(self.soundButtonsCanvas)
            self.soundButtonsCanvas.addWidget(self.buttonTabsCanvas)
            self.buttonsIndex = buttonIndex
            for _tabItem in self.buttonsIndex:
                tabScrollableArea = QScrollArea()
                tabScrollableArea.setWidgetResizable(True)
                tabCanvas = QWidget()
                tabContents = QHBoxLayout()
                tabContents.addStretch(0)
                buttonColumnCanvas = QVBoxLayout()
                buttonColumnCounter = 0
                for _buttonName in self.buttonsIndex[_tabItem]:
                    button = AudioButton(self.progenitor, _buttonName)
                    if buttonColumnCounter < Settings['MaxRows']:
                        buttonColumnCanvas.addWidget(button)
                        buttonColumnCounter += 1
                    else:
                        # buttonColumnCanvas.addStretch(0) # commented out for dynamic sized audio buttons.
                        tabContents.addLayout(buttonColumnCanvas)
                        buttonColumnCanvas = QVBoxLayout()
                        buttonColumnCanvas.addWidget(button)
                        buttonColumnCounter = 1 ## 1 since i added a button from overflow of prev column
                else:
                    # buttonColumnCanvas.addStretch(0) # commented out for dynamic sized audio buttons.
                    tabContents.addLayout(buttonColumnCanvas)
                    tabContents.addStretch(0)
                    tabCanvas.setLayout(tabContents)
                    rich.print(f"[PySoundboard] [green]Adding Column:[/green] Incomplete {str(buttonColumnCounter).rjust(2,"0")}/{Settings['MaxRows']} [magenta b]<{_tabItem}>[/magenta b]") if buttonColumnCounter < Settings['MaxRows'] else rich.print(f'[PySoundboard] [green]Adding Column: Completed MaxRow[/green] [magenta b]<{_tabItem}>[/magenta b]')
                    tabScrollableArea.setWidget(tabCanvas)
                    self.buttonTabsCanvas.addTab(tabScrollableArea, _tabItem)
            self.progenitor.soundboardTab.soundButtonsRefreshListButton.setDisabled(False)
            self.refreshButtonDisplayLabel.setHidden(True)
        def refreshButtons(self):
            self.progenitor.soundboardTab.soundButtonsRefreshListButton.setDisabled(True)
            self.refreshButtonDisplayLabel.setHidden(False)
            self._RebakeButtonsThreadingWrapper()
            self.buttonTabsCanvas.deleteLater()
    class SlotStatusMonitor(QGroupBox):
        def __init__(self, title, parent:"MainWindow"=None):
            super().__init__(title, parent)
            self.slotStatusMonitorCanvas = QVBoxLayout()
            self.progenitor = parent
            self.setLayout(self.slotStatusMonitorCanvas)
            for slot in range(0, AudioSystem.audioPoolSize):
                self.slotStatusMonitorCanvas.addWidget(self._SlotDisplay(slot, self.progenitor))
        class _SlotDisplay(QWidget):
            def __init__(self, slotNumber, parent:"MainWindow"):
                super().__init__(parent)
                self.slot = slotNumber
                self.slotVCanvas = QVBoxLayout()
                self.setLayout(self.slotVCanvas)
                self.slotInformationText = QLabel()
                self.setFixedHeight(80)
                self.slotControlButtons = QHBoxLayout()
                self.slotInformationText.setWordWrap(True)
                self.slotInformationText.setMinimumSize(600,38)
                self.slotVCanvas.addWidget(self.slotInformationText)
                self.slotVCanvas.addLayout(self.slotControlButtons)
                parent.updaterLoop.appendToQueue(self.slotStatusUpdater)
                self.slotControlButtons.addWidget(FuncButton('Looping', self.toggleLoop, parent.buttonSize[0]))
                self.slotControlButtons.addWidget(FuncButton('Resume', self.resume, parent.buttonSize[0]))
                self.slotControlButtons.addWidget(FuncButton('Pause', self.pause, parent.buttonSize[0]))
                self.slotControlButtons.addWidget(FuncButton('Stop', self.stop, parent.buttonSize[0]))
                self.slotControlButtons.addWidget(FuncButton('Unload', self.unload, parent.buttonSize[0]))
                self.slotControlButtons.addStretch(0)
            def slotStatusUpdater(self):
                slot:PSbHelper.AudioMedia = AudioSystem.audioPool['audio'][self.slot]
                name, src, mediastat, loopstat, playstat, playrate = slot.getStatus()
                _text = f'[Slot {name}] - {mediastat if src == '' else src}{f"\n : {loopstat}" if loopstat != '' else '\n'}{f" : {mediastat}" if src != '' else ''} : {playstat} [@ {playrate}x]'
                self.slotInformationText.setText(_text)
            def toggleLoop(self):
                AudioSystem.toggleLoopAudioMediaSlot('audio', self.slot)
            def resume(self):
                AudioSystem.playSlot('audio', self.slot)
            def pause(self):
                AudioSystem.pauseSlot('audio', self.slot)
            def stop(self):
                AudioSystem.stopSlot('audio', self.slot)
            def unload(self):
                AudioSystem.unloadAudioMediaSlot('audio', self.slot)
    class DebugMonitor(QGroupBox):
        def __init__(self, title, parent:"MainWindow"=None):
            super().__init__(title, parent)
            self.progenitor = parent
            self.debugScrollableCanvas = QScrollArea()
            self.debugCanvas = QVBoxLayout()
            self.debugScrollableCanvas.setWidgetResizable(True)
            self.debugCanvas.addWidget(FuncButton('refreshButtons', self.progenitor.soundboardTab.soundButtonsRefreshListButton.clicked.emit))
            self.debugCanvas.addWidget(self.debugScrollableCanvas)
            self.setLayout(self.debugCanvas)
            self.debugInfoLabel = QLabel()
            self.debugScrollableCanvas.setWidget(self.debugInfoLabel)
            self.debugInfoLabel.setWordWrap(True)
            self.progenitor.updaterLoop.appendToQueue(self.updateDebugLabel)
        def updateDebugLabel(self):
            debugText:str = ''
            mediaPool, index = AudioSystem.status(False)
            for pool in mediaPool:
                debugText += pool
            debugText += index
            self.debugInfoLabel.setText(f"AudioSystem.audioIndex[AUDIO_MEDIA] Size: {len(AudioSystem.audioIndex[PSbHelper.SoundType.AUDIO_MEDIA])} Sounds\n{debugText}")
    class PySoundboardSettings(QGroupBox):
        def __init__(self, title, parent=None):
            super().__init__(title, parent)
# Ai Assisted, Keyfilter code START
class ArrowKeysFilter_Callback(QObject):
    def __init__(self, callback):
        super().__init__()
        if not callable(callback):
            raise TypeError(f"{callback} Not Calllable Method")
        self.callback = callback
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            match event.key():
                case Qt.Key.Key_Left | Qt.Key.Key_Right | Qt.Key.Key_Up | Qt.Key.Key_Down:
                    rich.print('[PySoundboard] KeyPress: <ARROW_KEY>')
                    self.callback()
        return False   
# Ai Assisted, Keyfilter code END
## Define Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.buttonSize = [120, 30]
        self.updaterLoop = updateTimerQueue(self, 125)
        self.updaterLoop.appendToQueue(self._updateTopBarTitle)
        self.setWindowTitle('PySoundboard PyQt6 GUI')
#         self.setObjectName('baseCanvas')
#         ## To keep ASPECT_RATIO use:
#         # background-image: url(image.png);
#         self.setStyleSheet("""
#     QWidget#baseCanvas {
#         border-image: url(test.png) 0 0 0 0 stretch stretch;
#         background-position: center;
#         }
# """)
        # Set adressable space
        BaseCanvas = QWidget()
        self.setCentralWidget(BaseCanvas)
        # Main adressable space
        VerticalCanvas = QVBoxLayout()
        BaseCanvas.setLayout(VerticalCanvas)
        # GUI sections
        topBarCanvas = QHBoxLayout()
        self.topBarStatus = QLabel()
        topBarCanvas.addWidget(QLabel("PySoundboard PyQt6 - @junkynioy"))
        topBarCanvas.addWidget(self.topBarStatus)
        self.topBarStatus.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.topBarStatus.setWordWrap(True)
        self.topBarStatus.setMinimumSize(600,38)
        self.topBarStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.audioDeviceControlsGroup = QGroupBox('')
        self.mediaControlsGroup = QGroupBox('')
        self.soundboardTabsGroup = QTabWidget()
        VerticalCanvas.addLayout(topBarCanvas)
        # such big brain use of dictionary
        widgets = {self.audioDeviceControlsGroup:0, self.mediaControlsGroup:0, self.soundboardTabsGroup:1}
        for widget in widgets:
            VerticalCanvas.addWidget(widget, widgets.get(widget))
        else:
            self.bakeGroupContents()
        # VerticalCanvas.addStretch(1)
    def bakeGroupContents(self):
        self._audioDeviceControlsContent()
        self._mediaControlsContent()
        self._soundboardTabsContent()
    def _updateTopBarTitle(self):
        if self.mediaSlotSelector.currentIndex() >= AudioSystem.audioPoolSize:
            return
        name, src, mediastat, loopstat, playstat, playrate = AudioSystem.audioPool['audio'][self.mediaSlotSelector.currentIndex()].getStatus()
        _text = f'[Slot {name} - {mediastat if src == '' else src}{f" : {loopstat}" if loopstat != '' else ''}{f" : {mediastat}" if src != '' else ''} : {playstat} @ {playrate}x]'
        self.topBarStatus.setText(_text)
    def _audioDeviceControlsContent(self):
        audioDeviceCanvas = QHBoxLayout()
        self.audioDeviceControlsGroup.setLayout(audioDeviceCanvas)
        audioDeviceCanvas.addStretch(1)
        # Audio Device Select Combo Box START
        audioDeviceSelectCanvas = QVBoxLayout()
        self.audioDeviceSelectComboBox = QComboBox()
        audioDeviceSelectCanvas.addStretch(1)
        audioDeviceSelectCanvas.addWidget(QLabel("Current Device:"))
        audioDeviceSelectCanvas.addWidget(self.audioDeviceSelectComboBox)
        def _changeDevice():
            def _getDevice():
                devices = QMediaDevices.audioOutputs()
                for device in devices:
                    if device.description() == self.audioDeviceSelectComboBox.currentText():
                        return device
            try:
                UpdateSettings("AudioDevice",self.audioDeviceSelectComboBox.currentText())
                AudioSystem.setDevice(_getDevice(), True)
                AudioSystem.loadAudioMedia('audio','startup',0)
                AudioSystem.playSlot('audio',0)
                splashCli()
                rich.print(f"[PySoundboard] <{f'Default Device"{Settings["AudioDevice"]}"' if Settings["AudioDevice"] is None else self.audioDeviceSelectComboBox.currentText()}> Found!\n[PySoundboard] Successfully Bound to Device!")
            except Exception as ERR:
                splashCli()
                rich.print('[PySoundboard] System Defaulting!')
                UpdateSettings("AudioDevice", None)
                AudioSystem.setDevice(QMediaDevices.defaultAudioOutput(), True)
                AudioSystem.loadAudioMedia('audio','startup',0)
                AudioSystem.playSlot('audio',0)
                rich.print(f"[PySoundboard] [{self.audioDeviceSelectComboBox.currentText()}] : {repr(ERR)}\n[PySoundboard] Restart Soundboard to refresh Dropdown List ") if self.audioDeviceSelectComboBox.currentIndex() != 0 else ''      
        self.audioDeviceSelectComboBox.setFixedSize(435, 42)
        self.audioDeviceSelectComboBox.setPlaceholderText('Defaulting, Select an Output Device...')
        self.audioDeviceSelectComboBox.addItems([device.description() for device in QMediaDevices.audioOutputs()])
        self.audioDeviceSelectComboBox.setCurrentIndex(self.audioDeviceSelectComboBox.findText(Settings["AudioDevice"]))
        self.audioDeviceSelectComboBox.activated.connect(_changeDevice)
        audioDeviceSelectCanvas.addStretch(1)
        audioDeviceCanvas.addLayout(audioDeviceSelectCanvas)
        # Audio Device Select Combo Box END
        # Audio Device Volume Control START
        def _changeVolume():
            Volume = int(self.audioDeviceVolumeSlider.value())
            self.audioDeviceVolumeLabel.setText(f"Volume: {Volume}%")
            AudioSystem.setVolume('audio', Volume)
        def _saveVolume():
            UpdateSettings("Volume", self.audioDeviceVolumeSlider.value())
        audioDeviceVolumeControlCanvas = QVBoxLayout()
        self.audioDeviceVolumeLabel = QLabel(f"Volume: {Settings.get('Volume')}%")
        audioDeviceVolumeControlCanvas.addWidget(self.audioDeviceVolumeLabel)
        self.audioDeviceVolumeSlider = QSlider(Qt.Orientation.Horizontal)
        self.audioDeviceVolumeSlider.setFixedSize(260,11)
        self.audioDeviceVolumeSlider.setRange(0, 100)
        audioDeviceVolumeControlCanvas.addWidget(self.audioDeviceVolumeSlider)
        self.audioDeviceVolumeSlider.setValue(int(Settings['Volume']))
        self.audioDeviceVolumeSlider.valueChanged.connect(_changeVolume)
        ### KeyFilter Event, Ai Assisted code START
        self.arrowKeys_saveVolume = ArrowKeysFilter_Callback(_saveVolume)
        self.audioDeviceVolumeSlider.installEventFilter(self.arrowKeys_saveVolume)
        ### Keyfilter Event, Ai Assisted code END
        self.audioDeviceVolumeSlider.sliderReleased.connect(_saveVolume)
        audioDeviceCanvas.addLayout(audioDeviceVolumeControlCanvas)
        # Audio Device Volume Control END
        # Audio Device Global PlaybackSpeed START
        audioDevicePlaySpeedCanvas = audioDeviceVolumeControlCanvas
        def _changeSpeed():
            ###
            # ADD CHECK TO SEE IF SLOT IS PLAYING, IF IT ISNT, IGNORE SLOT
            ###
            self.audioDeviceSpeedLabel.setText(f"Playback Speed: {self.audioDeviceSpeedSlider.value()/100}x")
            for slot in range(0, AudioSystem.audioPoolSize):
                AudioSystem.setSlotPlaybackSpeed('audio', slot, self.audioDeviceSpeedSlider.value()/100)
        def _speedSpeedToggle():
            self.audioDeviceSpeedSlider.setDisabled(not self.audioDeviceSpeedSyncToggle.isChecked())
            rich.print("[PySoundboard] PlaybackSpeed Sync:", self.audioDeviceSpeedSyncToggle.isChecked())
            for slot in range(0, AudioSystem.audioPoolSize):
                AudioSystem.setSlotPlaybackSpeed('audio', slot, 1) if not self.audioDeviceSpeedSyncToggle.isChecked() else AudioSystem.setSlotPlaybackSpeed('audio', slot, self.audioDeviceSpeedSlider.value()/100)
        self.audioDeviceSpeedSlider = QSlider(Qt.Orientation.Horizontal)
        audioDeviceSpeedLabelCanvas = QHBoxLayout() # main canvas
        audioDeviceSpeedSyncToggleCanvas = QHBoxLayout() # canvas for speed display + sync toggle
        self.audioDeviceSpeedLabel = QLabel('Playback Speed: 1.00x')
        self.audioDeviceSpeedSyncToggle = QRadioButton()
        self.audioDeviceSpeedSyncToggle.setCheckable(True)
        self.audioDeviceSpeedSyncToggle.setChecked(True)
        self.audioDeviceSpeedSyncToggle.clicked.connect(_speedSpeedToggle)
        audioDeviceSpeedSyncToggleCanvas.addWidget(self.audioDeviceSpeedSyncToggle) # add toggle to speedsynccanvas
        audioDeviceSpeedSyncToggleCanvas.addWidget(QLabel('Sync')) # add toggle label for sync to speedsynccanvas
        audioDeviceSpeedLabelCanvas.addLayout(audioDeviceSpeedSyncToggleCanvas) # sync toggle + speed label to speedlabelcanvas
        audioDeviceSpeedLabelCanvas.addWidget(self.audioDeviceSpeedLabel) # add speed display to speedlabelcanvas
        audioDeviceSpeedLabelCanvas.addStretch(1)
        audioDevicePlaySpeedCanvas.addLayout(audioDeviceSpeedLabelCanvas) # add to main canvas
        audioDevicePlaySpeedCanvas.addWidget(self.audioDeviceSpeedSlider) # speed Slider
        self.audioDeviceSpeedSlider.setFixedHeight(11)
        self.audioDeviceSpeedSlider.setRange(5, 500)
        self.audioDeviceSpeedSlider.setValue(100)
        self.audioDeviceSpeedSlider.valueChanged.connect(_changeSpeed)
        # Audio Device Global PlaybackSpeed END
        # Audio Device Global Toggles START
        audioDeviceToggles = QVBoxLayout()
        def _toggleGlobalLoopMode():
            self.audioDeviceLoopButton.setText(f'Looping ALL {'ON' if self.audioDeviceLoopButton.isChecked() else 'OFF'}')
            for slot in range(0, AudioSystem.audioPoolSize):
                slotLoopingState = AudioSystem.audioPool['audio'][slot].loops() > 1
                if not slotLoopingState is self.audioDeviceLoopButton.isChecked():
                    AudioSystem.toggleLoopAudioMediaSlot('audio', slot)
        def _toggleMultiMode():
            self.mediaControlAllSlots.setChecked(self.audioDeviceMultiButton.isChecked())
            self.mediaControlAllSlots.clicked.emit()
            self.mediaControlAllSlots.setDisabled(self.audioDeviceMultiButton.isChecked())
            self.mediaControlAllSlots.setToolTip('MultiMode is Enabled!' if self.audioDeviceMultiButton.isChecked() else '')
            self.audioDeviceMultiButton.setText(f"Multi-Mode {'ON' if self.audioDeviceMultiButton.isChecked() else 'OFF'}")
        self.audioDeviceLoopButton = FuncButton(f'Looping ALL OFF', _toggleGlobalLoopMode, self.buttonSize[0], self.buttonSize[1])
        self.audioDeviceLoopButton.setCheckable(True)
        self.audioDeviceMultiButton = FuncButton('Multi-Mode OFF', _toggleMultiMode, h=29)
        self.audioDeviceMultiButton.setCheckable(True)
        audioDeviceToggles.addWidget(self.audioDeviceLoopButton)
        audioDeviceToggles.addWidget(self.audioDeviceMultiButton)
        audioDeviceCanvas.addLayout(audioDeviceToggles)
        # Audio Device Global Toggles END
        audioDeviceCanvas.addStretch(1)
    def _mediaControlsContent(self):
        mediaControlsCanvas = QHBoxLayout()
        mediaControlsCanvas.addStretch(1)
        self.mediaControlsGroup.setLayout(mediaControlsCanvas)
        # Control ALL slots START
        def _controlAllSlots():
            toolTip = '"All Slots" is Enabled.' if self.mediaControlAllSlots.isChecked() else ''
            self.mediaLoopSlot.setToolTip(f"{toolTip} Use \"Looping ALL\"")
            self.mediaLoopSlot.setDisabled(self.mediaControlAllSlots.isChecked())
            self.mediaSlotSelector.setToolTip(toolTip)
            self.mediaSlotSelector.setDisabled(self.mediaControlAllSlots.isChecked())
        self.mediaControlAllSlots = FuncButton('All Slots', w=self.buttonSize[0]//2, h=self.buttonSize[1])
        self.mediaControlAllSlots.setCheckable(True)
        self.mediaControlAllSlots.clicked.connect(_controlAllSlots)
        mediaControlsCanvas.addWidget(self.mediaControlAllSlots)
        # Control ALL slots END
        # Select Slot START
        self.mediaSlotSelector = QComboBox()
        self.mediaSlotSelector.addItems([f"Slot {slot.name}" for slot in AudioSystem.audioPool['audio']])
        self.mediaSlotSelector.setFixedHeight(30)
        mediaControlsCanvas.addWidget(self.mediaSlotSelector)
        # Select Slot END
        # Play Resume Stop Button START
        ######## DESYNC BUG OF SLOTS WHEN "ALL SLOTS" IS SELECTED, AFTER PAUSING/RESUMING ONLY 1 SLOT TODO
        def _toggleAllPlayPauseState():
            PSbHelper.togglePlaybackStateAll(AudioSystem) if self.mediaControlAllSlots.isChecked() else PSbHelper.togglePlaybackStateSlot(AudioSystem, self.mediaSlotSelector.currentIndex())
        def _stopAllPlayback():
            AudioSystem.unloadAllAudioMedia() if self.mediaControlAllSlots.isChecked() else AudioSystem.unloadAudioMediaSlot('audio', self.mediaSlotSelector.currentIndex())
        self.mediaResumePauseButton = FuncButton('Resume / Pause', _toggleAllPlayPauseState, w=self.buttonSize[0], h=self.buttonSize[1])
        self.mediaStopButton = FuncButton('Stop', _stopAllPlayback, self.buttonSize[0]//2,self.buttonSize[1])
        mediaControlsCanvas.addWidget(self.mediaResumePauseButton)
        mediaControlsCanvas.addWidget(self.mediaStopButton)
        # Play Resume Stop Button END
        # Media position START
        def _updateMediaPositionSlider():
            _, dur, pos = AudioSystem.audioMediaPos('audio',self.mediaSlotSelector.currentIndex())
            self.mediaCurrentPositionSlider.setRange(0, int(dur))
            self.mediaCurrentPositionSlider.setValue(int(pos)) if not self._pauseMediaPosUpdate else ''
        def _seekMedia():
            AudioSystem.audioPool['audio'][self.mediaSlotSelector.currentIndex()].setPosition(self.mediaCurrentPositionSlider.value()*1000)
            self._pauseMediaPosUpdate = False
        def _pauseMedia():
            self._pauseMediaPosUpdate = True
        def _updatePosDisplay(): 
            pos = self.mediaCurrentPositionSlider.value()
            self.mediaElapsedTimeLabel.setText(f"{pos} s" if pos < 60 else f"{round(pos/60,2)} min")
        self._pauseMediaPosUpdate = False
        self.mediaCurrentPositionSlider = QSlider(Qt.Orientation.Horizontal)
        self.mediaCurrentPositionSlider.setFixedWidth(245)
        self.updaterLoop.appendToQueue(_updateMediaPositionSlider)
        self.mediaCurrentPositionSlider.sliderPressed.connect(_pauseMedia)
        self.mediaCurrentPositionSlider.sliderMoved.connect(_updatePosDisplay)
        self.mediaCurrentPositionSlider.sliderReleased.connect(_seekMedia)
        mediaControlsCanvas.addWidget(self.mediaCurrentPositionSlider)
        # Media position END
        # Elapsed time START
        self.mediaElapsedTimeLabel = QLabel('---')
        self.mediaElapsedTimeLabel.setFixedWidth(135)
        def _updateElapsedTimeDisplay():
            self.mediaElapsedTimeLabel.setText(AudioSystem.audioMediaPos('audio', self.mediaSlotSelector.currentIndex(), True)) if not self._pauseMediaPosUpdate else ''
        self.updaterLoop.appendToQueue(_updateElapsedTimeDisplay)
        mediaControlsCanvas.addWidget(self.mediaElapsedTimeLabel)
        # Elapsed time END
        # Slot Loop START
        def _loopSlot():
            AudioSystem.toggleLoopAudioMediaSlot('audio', self.mediaSlotSelector.currentIndex())
        self.mediaLoopSlot = FuncButton("Toggle Loop", _loopSlot, self.buttonSize[0], self.buttonSize[1])
        mediaControlsCanvas.addWidget(self.mediaLoopSlot)
        # Slot Loop END
        mediaControlsCanvas.addStretch(1)
    def _soundboardTabsContent(self):
        # might not need a self var some of these
        self.soundboardTab = sections.SoundButtons('', self)
        self.slotsMonitorTab = sections.SlotStatusMonitor('', self)
        self.appSettingsTab = sections.PySoundboardSettings('', self)
        self.debugMonitor = sections.DebugMonitor('', self) if Settings.get('DebugInfo') else ''
        
        self.soundboardTabsGroup.addTab(self.soundboardTab, 'Soundboard')
        self.soundboardTabsGroup.addTab(self.slotsMonitorTab, 'Slots')
        self.soundboardTabsGroup.addTab(self.appSettingsTab, 'Settings')
        self.soundboardTabsGroup.addTab(self.debugMonitor, 'debugMonitor') if Settings.get('DebugInfo') else ''
    def handHeldMode(self, bool:bool):
        if bool:
            print('deckMode_enabled')
    ## Ai Assisted Window centering
    ## Unknown if Cross Platform
    def center_window(self):
        screen = self.screen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())
class FuncButton(QPushButton):
    def __init__(self, name:str, callback=None, w:int|None=None, h:int|None=None, styleSheet:str|None=None):
        super().__init__()
        self.setText(name)
        self.setStyleSheet(f"padding: 5%;{f' {styleSheet}' if styleSheet else ''}") #  margin: 0%; ; 
        self.setFixedWidth(w) if w else ''
        self.setFixedHeight(h) if h else ''
        if callback is None:
            return
        if not callable(callback):
            raise TypeError(f'"{callback}" is Non-Callable')
        self.clicked.connect(callback)
class AudioButton(FuncButton):
    def __init__(self, parent:MainWindow, name):
        self.name = name
        self.progenitor = parent
        super().__init__(name, self.play, w=130, h=28, styleSheet='text-align: left;')
        self.setToolTip(name)
    def play(self):
        multiMode = self.progenitor.audioDeviceMultiButton.isChecked()
        AudioSystem.loadAudioMedia('audio', self.name, None if multiMode else self.progenitor.mediaSlotSelector.currentIndex())
        AudioSystem.playAll() if multiMode else AudioSystem.playSlot('audio', self.progenitor.mediaSlotSelector.currentIndex())
# Load Settings
Settings:dict = PSbHelper.InitializeSettings()
setAppTheme(Settings['UseSystemTheme'])
splashInfo(Settings.get('Splash'))
# Initialize System
AudioSystem = PSbHelper.InitializeAudioSystem(Settings); AudioSystem.togglePoolRollOver('audio')
# Start Window
Main = MainWindow(); Main.show(); Main.center_window() if os.name=='nt' else ''
Main.handHeldMode(Settings['HandHeld'])
AudioSystem.addIndex(PSbHelper.SoundType.AUDIO_MEDIA,'./startup.wav')
AudioSystem.loadAudioMedia('audio','startup',0)
AudioSystem.playSlot('audio',0)
sys.exit(APP.exec())