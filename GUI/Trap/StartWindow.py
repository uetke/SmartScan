'''
Created on 18 sep. 2015

@author: carattino
'''

from pyqtgraph.Qt import QtCore, QtGui

class StartWindow(QtGui.QMainWindow):
    """ Window that will contain the main controllers for the trap.
    """
    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI()
        self.time = _session.time
        self.accuracy = _session.accuracy

    def initUI(self):

        self.power_spectra = Power_Spectra()
        self.conf_times = ConfigureTimes()
        self.monitor_values = monitor_values()
        self.timetraces = TimeTraces()
        self.apd_timetrace = Apd_Timetrace()

        QtCore.QObject.connect(self.monitor_values, QtCore.SIGNAL('TimeTraces'),self.timetraces.updateTimes)
        QtCore.QObject.connect(self.power_spectra, QtCore.SIGNAL('Stop_Tr'),self.monitor_values.stop_timer)


        self.setCentralWidget(self.monitor_values)
        self.setGeometry(450,30,550,900)
        self.setWindowTitle('Monitor')
#         self.connect(self.conf_times,  QtCore.SIGNAL("Times"),self.power_spectra.updateTimes)
        QtCore.QObject.connect(self.conf_times.run_button, QtCore.SIGNAL('clicked()'),self.power_spectra.update)
#
        saveAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/floppy-icon.png'),'Save',self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save the displayed data')
        saveAction.triggered.connect(self.power_spectra.fileSave)

        exitAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/Signal-stop-icon.png'),'Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit the program in a safe way')
        exitAction.triggered.connect(self.power_spectra.exit_safe)

        configureTimes = QtGui.QAction(QtGui.QIcon('GUI/Icons/pinion-icon.png'),'Configure',self)
        configureTimes.setShortcut('Ctrl+T')
        configureTimes.setStatusTip('Configure the acquisition times')
        configureTimes.triggered.connect(self.conf_times.show)

        runMonitor = QtGui.QAction('Run Monitor',self)
        runMonitor.setShortcut('Ctrl+R')
        runMonitor.setStatusTip('Starts running the monitor of signals')
        runMonitor.triggered.connect(self.monitor_values.start_timer)

        stopMonitor = QtGui.QAction('Stop Monitor',self)
        stopMonitor.setStatusTip('Stops running the monitor of signals')
        stopMonitor.triggered.connect(self.monitor_values.stop_timer)

        showTimetraces = QtGui.QAction('Show Timetraces',self)
        showTimetraces.setStatusTip('Shows plots for timetraces')
        showTimetraces.triggered.connect(self.timetraces.show)

        acquireTimetrace = QtGui.QAction('Acquire timetrace',self)
        acquireTimetrace.setStatusTip('Starts acquiring fast timetraces')
        acquireTimetrace.triggered.connect(self.power_spectra.show)

        triggerTimetrace = QtGui.QAction('Start acquiring timetraces',self)
        triggerTimetrace.setStatusTip('Click tu run the high priority ADwin process')
        triggerTimetrace.triggered.connect(self.power_spectra.update)

        stopTimetrace = QtGui.QAction('Stop timetrace',self)
        stopTimetrace.setStatusTip('Stops the acquisition after the current')
        stopTimetrace.triggered.connect(self.power_spectra.stop_acq)

        showAPD = QtGui.QAction('APD',self)
        showAPD.setStatusTip('Shows the window for high time resolution APD timetrace')
        showAPD.triggered.connect(self.apd_timetrace.show)

        triggerAPD = QtGui.QAction('Trigger APD',self)
        triggerAPD.setStatusTip('Triggers time resolution APD timetrace')
        triggerAPD.triggered.connect(self.apd_timetrace.start_timetrace)

        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        confgMenu = menubar.addMenu('&Configure')
        confgMenu.addAction(configureTimes)

        monitorMenu = menubar.addMenu('&Monitor')
        monitorMenu.addAction(showTimetraces)
        monitorMenu.addAction(runMonitor)
        monitorMenu.addAction(stopMonitor)

        traceMenu = menubar.addMenu('&Timetraces')
        traceMenu.addAction(acquireTimetrace)
        traceMenu.addAction(triggerTimetrace)
        traceMenu.addAction(stopTimetrace)

        apdMenu = menubar.addMenu('&APD')
        apdMenu.addAction(showAPD)
        apdMenu.addAction(triggerAPD)

    def closeEvent(self, event):
        _session.adw.stop(10)
        _session.adw.stop(9)
        event.accept()

if __name__ == '__main__':
    pass
