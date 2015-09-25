'''
Created on 18 sep. 2015

@author: aj carattino
'''
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import sys
import pyqtgraph as pg
from PyQt4.Qt import QApplication
from datetime import datetime
import os
import _session
from GUI.Trap.APD import APD
from GUI.Trap.PowerSpectra import PowerSpectra
from GUI.Trap.ConfigWindow import ConfigWindow
from lib.xml2dict import variables

import copy

class Monitor(QtGui.QMainWindow):
    """ Monitor of the relevant signals.
    """
    def __init__(self,parent=None):
        super(Monitor,self).__init__()
        self.setWindowTitle('Signal Monitor')
        self.setGeometry(30,30,1200,900)

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
        self.t =[]
        self.data = []
        for i in range(len(self.devices)):
            self.t.append(np.zeros([1,]))
            self.data.append(np.zeros([1,]))


        self.varx = self.timetraces.qpdx.plot(self.t[0],self.data[0],pen='y')
        self.vary = self.timetraces.qpdy.plot(self.t[1],self.data[1],pen='y')
        self.varz = self.timetraces.qpdz.plot(self.t[2],self.data[1],pen='y')
        self.vard = self.timetraces.diff.plot(self.t[3],self.data[2],pen='y')
        self.vara = self.timetraces.apd1.plot(self.t[4],self.data[3],pen='y')
        self.varl = self.timetraces.lock.plot(self.t[5],self.data[3],pen='y')

        self.fifo=variables('Fifo')
        self.fifo_name = ''
        self.ctimer = QtCore.QTimer()
        self.running = False
        self.delay=400*0.1e-3

        QtCore.QObject.connect(self.ctimer,QtCore.SIGNAL("timeout()"),self.updateMon)
        QtCore.QObject.connect(self,QtCore.SIGNAL("TimeTraces"),self.updateTimes)
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

        acquireTimetrace = QtGui.QAction('Power Spectra',self)
        acquireTimetrace.setStatusTip('Show the Power Spectra window')
        acquireTimetrace.triggered.connect(self.PowerSpectra.show)

        triggerTimetrace = QtGui.QAction('Start acquiring timetraces',self)
        triggerTimetrace.setStatusTip('Click tu run the high priority ADwin process')
        triggerTimetrace.triggered.connect(self.PowerSpectra.update)

        stopTimetrace = QtGui.QAction('Stop timetrace',self)
        stopTimetrace.setStatusTip('Stops the acquisition after the current')
        stopTimetrace.triggered.connect(self.PowerSpectra.stop_acq)

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
        for i in range(len(self.devices)):
            fifo_name = '%s%i' %(self.devices[i].properties['Type'],self.devices[i].properties['Input']['Hardware']['PortID'])
            data = copy.copy(np.array([_session.adw.get_fifo(self.fifo.properties[fifo_name])]))
            calibration = self.devices[i].properties['Input']['Calibration']
            data = np.array((data-calibration['Offset'])/calibration['Slope'])
            final_data.append(data)
        self.emit( QtCore.SIGNAL('TimeTraces'), final_data)

    def updateTimes(self,data):
        """ Updates the plots of the variances.
        """
        #Check the sizes of the variances
        var = copy.copy(data)
        for i in range(len(var)):
            xdata = np.arange(len(var[i][0]))*self.delay
            old_data = self.data[i]
            old_t = self.t[i]
            self.t[i] = np.append(self.t[i],xdata+max(self.t[i])+self.delay)
            self.data[i] = np.append(self.data[i],var[i])
            limit = _session.timetrace_time/self.delay
            self.t[i] = self.t[i][-limit:]
            self.data[i] = self.data[i][-limit:]

        self.varx.setData(self.t[0],self.data[0])
        self.vary.setData(self.t[1],self.data[1])
        self.varz.setData(self.t[2],self.data[2])
        self.vard.setData(self.t[3],self.data[3])
        self.vara.setData(self.t[4],self.data[4])
        self.varl.setData(self.t[5],self.data[5])

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

    def fileSave(self):
        """Saves the files to a specified folder.
        """
        name = 'Timetrace_Data'
        savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        i=1
        filename = name
        while os.path.exists(savedir+filename+".dat"):
            filename = '%s_%s' %(name,i)
            i += 1
        filename = filename+".dat"
        np.savetxt("%s%s" %(savedir,filename), self.data,fmt='%s', delimiter=",")
        print('Data saved in %s'%(savedir+filename) )
        return

    def exit_safe(self):
        """ Exits the application.
        """
        if self.PowerSpectra.is_running:
            self.PowerSpectra.exit_safe()
        if self.APD.is_running:
            self.APD.exit_safe()
        self.ConfigWindow.close()
        self.stop_timer()
        self.close()

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
        qpdx.setLabel('bottom', "Time", units='s')
        qpdy.setLabel('left', "QPD Y", units='V')
        qpdy.setLabel('bottom', "Time", units='s')
        qpdz.setLabel('left', "QPD Z", units='V')
        qpdz.setLabel('bottom', "Time", units='s')
        diff.setLabel('left', "Diff", units='V')
        diff.setLabel('bottom', "Time", units='s')
        apd1.setLabel('left','APD', units = 'CPS')
        apd1.setLabel('bottom','Time',units='s')
        lock.setLabel('left','Lock-In', units = 'V')
        lock.setLabel('bottom','Time',units='s')
        self.qpdx = qpdx
        self.qpdy = qpdy
        self.qpdz = qpdz
        self.diff = diff
        self.apd1 = apd1
        self.lock = lock

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
