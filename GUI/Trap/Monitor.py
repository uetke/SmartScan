'''
Created on 18 sep. 2015

@author: aj carattino
'''
import numpy as np
from pyqtgraph.Qt import QtGui
import sys
import pyqtgraph as pg
from PyQt4.Qt import QApplication

from GUI.Trap.APD import APD
from GUI.Trap.PowerSpectra import PowerSpectra
from GUI.Trap.ConfigWindow import ConfigWindow

class Monitor(QtGui.QMainWindow):
    """ Monitor of the relevant signals.
    """
    def __init__(self,parent=None):
        super(Monitor,self).__init__()
        self.setWindowTitle('Signal Monitor')
        self.setGeometry(30,30,550,900)

        self.timetraces = MonitorWidget()
        self.APD = APD()
        self.PowerSpectra = PowerSpectra()
        self.ConfigWindow = ConfigWindow()

        self.setCentralWidget(self.timetraces)

        # The devices to analize
        self.devices = []
        self.devices.append(_session.device['qpdx'])
        self.devices.append(_session.device['qpdy'])
        self.devices.append(_session.device['qpdz'])
        self.devices.append(_session.device['monitor'])
        self.devices.append(_session.device['apd1'])
        self.devices.append(_session.device['lock'])

        # Initial timetrace data
        self.var = np.zeros([6,250])
        x = np.arange(np.size(self.var,axis=1))

        self.varx = self.timetraces.qpdx.plot(x,self.var[0,:],pen='y')
        self.vary = self.timetraces.qpdy.plot(x,self.var[1,:],pen='y')
        self.varz = self.timetraces.qpdz.plot(x,self.var[1,:],pen='y')
        self.vard = self.timetraces.diff.plot(x,self.var[2,:],pen='y')
        self.vara = self.timetraces.apd1.plot(x,self.var[3,:],pen='y')
        self.varl = self.timetraces.lock.plot(x,self.var[3,:],pen='y')

        self.fifo=variables('Fifo')
        self.fifo_name = ''
        self.ctimer = QtCore.QTimer()
        self.running = False
        QtCore.QObject.connect(self.ctimer,QtCore.SIGNAL("timeout()"),self.updateMon)
        QtCore.QObject.connect(self.PowerSpectra, QtCore.SIGNAL('Stop_Tr'),self.stop_timer)
        QtCore.QObject.connect(self.APD, QtCore.SIGNAL('Stop_Tr'),self.stop_timer)


        ###################
        # Define the menu #
        ###################

        saveAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/floppy-icon.png'),'Save',self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save the displayed data')
        saveAction.triggered.connect(self.fileSave)

        exitAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/Signal-stop-icon.png'),'Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit the program in a safe way')
        exitAction.triggered.connect(self.exit_safe)

        configureTimes = QtGui.QAction(QtGui.QIcon('GUI/Icons/pinion-icon.png'),'Configure',self)
        configureTimes.setShortcut('Ctrl+T')
        configureTimes.setStatusTip('Configure the acquisition times')
        configureTimes.triggered.connect(self.ConfigWindow.show)

        runMonitor = QtGui.QAction('Run Monitor',self)
        runMonitor.setShortcut('Ctrl+R')
        runMonitor.setStatusTip('Starts running the monitor of signals')
        runMonitor.triggered.connect(self.start_timer)

        stopMonitor = QtGui.QAction('Stop Monitor',self)
        stopMonitor.setStatusTip('Stops running the monitor of signals')
        stopMonitor.triggered.connect(self.stop_timer)

        acquireTimetrace = QtGui.QAction('Acquire timetrace',self)
        acquireTimetrace.setStatusTip('Starts acquiring fast timetraces')
        acquireTimetrace.triggered.connect(self.PowerSectra.show)

        triggerTimetrace = QtGui.QAction('Start acquiring timetraces',self)
        triggerTimetrace.setStatusTip('Click tu run the high priority ADwin process')
        triggerTimetrace.triggered.connect(self.PowerSectra.update)

        stopTimetrace = QtGui.QAction('Stop timetrace',self)
        stopTimetrace.setStatusTip('Stops the acquisition after the current')
        stopTimetrace.triggered.connect(self.PowerSectra.stop_acq)

        showAPD = QtGui.QAction('APD',self)
        showAPD.setStatusTip('Shows the window for high time resolution APD timetrace')
        showAPD.triggered.connect(self.APD.show)

        triggerAPD = QtGui.QAction('Trigger APD',self)
        triggerAPD.setStatusTip('Triggers time resolution APD timetrace')
        triggerAPD.triggered.connect(self.APD.start_timetrace)

        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        confgMenu = menubar.addMenu('&Configure')
        confgMenu.addAction(configureTimes)

        monitorMenu = menubar.addMenu('&Monitor')
        monitorMenu.addAction(runMonitor)
        monitorMenu.addAction(stopMonitor)

        traceMenu = menubar.addMenu('&Timetraces')
        traceMenu.addAction(acquireTimetrace)
        traceMenu.addAction(triggerTimetrace)
        traceMenu.addAction(stopTimetrace)

        apdMenu = menubar.addMenu('&APD')
        apdMenu.addAction(showAPD)
        apdMenu.addAction(triggerAPD)

    def updateMon(self):
        final_data = []
        mean_data = []
        for i in range(len(self.devices)):
            self.fifo_name = '%s%i' %(self.detector[i].properties['Type'],self.detector[i].properties['Input']['Hardware']['PortID'])
            data = np.array([self.adw.get_fifo(self.fifo.properties[self.fifo_name])])
            calibration = self.detector[i].properties['Input']['Calibration']
            data = (data-calibration['Offset'])/calibration['Slope']

            #final_data = np.vstack((xdata,data))
            name = _session.devices[i].properties['Name']
            if name == "Monitor +":
                mean_data.append(np.mean(data))
            elif name == "Monitor -":
                mean_data.append(np.mean(data))
            elif name == "Diff":
                mean_data.append(np.mean(data))
                final_data.append(data)
            elif name == "QPD X":
                mean_data.append(np.mean(data))
                final_data.append(data)
            elif name == "QPD Y":
                mean_data.append(np.mean(data))
                final_data.append(data)
            elif name == "QPD Z":
                mean_data.append(np.mean(data))
            elif name == "APD 1":
                final_data.append(data)
        self.emit( QtCore.SIGNAL('TimeTraces'), final_data)
        self.emit(QtCore.SIGNAL('Means'), mean_data)

    def updateTimes(self,data):
        """ Updates the plots of the variances.
        """

        #Check the sizes of the variances
        for i in range(len(data)):
            s = np.size(data[i])
            self.var[i,:] = np.roll(self.var[i],-s,axis=0)
            self.var[i,-s:] = variances[i]

        self.data = self.var
        x = np.arange(np.size(self.var,axis=1))
        self.varx.setData(x,self.var[2,:])
        self.vary.setData(x,self.var[1,:])
        self.varz.setData(x,self.var[1,:])
        self.vard.setData(x,self.var[0,:])
        self.vara.setData(x,self.var[3,:])
        self.varl.setData(x,self.var[1,:])

    def start_timer(self):
        """ Starts the timer with a predefined update interval.
        """
        if not self.running:
            if self.PowerSpectra.is_running or self.APD.is_running:
                print('Cant update while power spectra or APD is running.')
            else:
                # Starts the process inside the ADwin
                _session.adw.start(10)
                self.ctimer.start(100)
                self.running = True
        else:
            self.stop_timer()

    def stop_timer(self):
        """ Stops the refreshing and the ADwin monitor.
        """
        self.ctimer.stop()
        _session.adw.stop(10)
        self.running = False

class MonitorWidget(QtGui.QWidget):
    """ Widget for displaying the Timetraces.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)

        # Timetraces
        qpdx = pg.PlotWidget()
        qpdy = pg.PlotWidget()
        qpdz = pg.PlotWidget()
        diff = pg.PlotWidget()
        apd1 = pg.PlotWidget()
        lock = pg.PlotWidget()
        qpdx.setLabel('left', "QPD X", units='V')
        qpdx.setLabel('bottom', "time", units='Steps')
        qpdy.setLabel('left', "QPD Y", units='V')
        qpdy.setLabel('bottom', "time", units='Steps')
        qpdz.setLabel('left', "QPD Z", units='V')
        qpdz.setLabel('bottom', "time", units='Steps')
        diff.setLabel('left', "Diff", units='V')
        diff.setLabel('bottom', "time", units='Steps')
        apd1.setLabel('left','APD', units = 'CPS')
        apd1.setLabel('bottom','time',units='Steps')
        lock.setLabel('left','Lock-In', units = 'V')
        lock.setLabel('bottom','time',units='Steps')
        self.qpdx = qpdx
        self.qpdy = qpdy
        self.diff = diff
        self.apd1 = apd1

        # Layout
        self.layout = QtGui.QGridLayout(self)
        self.layout.addWidget(self.qpdx, 0, 0)
        self.layout.addWidget(self.qpdy, 0, 1)
        self.layout.addWidget(self.diff, 1, 0)
        self.layout.addWidget(self.qpdz, 1, 1)
        self.layout.addWidget(self.apd1, 2, 0)
        self.layout.addWidget(self.lock, 2, 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mon = TimeTraces()
    mon.show()
    sys.exit(app.exec_())
