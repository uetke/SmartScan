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
import json
import pickle
import os
import _session
from GUI.Trap.APD import APD
from GUI.Trap.PowerSpectra import PowerSpectra
from GUI.Trap.ConfigWindow import ConfigWindow
from GUI.Trap.value_monitor import ValueMonitor
from lib.xml2dict import variables
import math as m
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
        self.ValueMonitor = ValueMonitor()

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
        self.delay = m.floor(_session.monitor_timeresol/1000/_session.adw.time_low) # In Adwin units
        self.timeDelay = _session.monitor_timeresol/1000 # In seconds

        QtCore.QObject.connect(self.ctimer,QtCore.SIGNAL("timeout()"),self.updateMon)
        QtCore.QObject.connect(self,QtCore.SIGNAL("TimeTraces"),self.updateTimes)
        QtCore.QObject.connect(self.PowerSpectra, QtCore.SIGNAL('Stop_Tr'),self.stop_timer)
        QtCore.QObject.connect(self.APD, QtCore.SIGNAL('Stop_Tr'),self.stop_timer)
        QtCore.QObject.connect(self,QtCore.SIGNAL('MeanData'),self.ValueMonitor.UpdateValues)
        QtCore.QObject.connect(self.ConfigWindow,QtCore.SIGNAL('Times'),self.updateParameters)

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
        
        bootAdwin = QtGui.QAction('Boot Adwin',self)
        bootAdwin.setStatusTip('Boots the ADwin and loads needed binaries')
        bootAdwin.triggered.connect(self.bootAdwin)

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
        
        showValueMonitor = QtGui.QAction('Value Monitor',self)
        showValueMonitor.setShortcut('Ctrl+V')
        showValueMonitor.setStatusTip('Shows the Value Monitor')
        showValueMonitor.triggered.connect(self.ValueMonitor.show)

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
        fileMenu.addAction(bootAdwin)

        confgMenu = menubar.addMenu('&Configure')
        confgMenu.addAction(configureTimes)

        monitorMenu = menubar.addMenu('&Monitor')
        monitorMenu.addAction(runMonitor)
        monitorMenu.addAction(stopMonitor)
        monitorMenu.addAction(showValueMonitor)

        traceMenu = menubar.addMenu('&Timetraces')
        traceMenu.addAction(acquireTimetrace)
        traceMenu.addAction(triggerTimetrace)
        traceMenu.addAction(stopTimetrace)

        apdMenu = menubar.addMenu('&APD')
        apdMenu.addAction(showAPD)
        apdMenu.addAction(triggerAPD)
        
        ####
        # Define some parameters
        ####
        self.runningTimeResol = _session.monitor_timeresol

    def updateMon(self):
        final_data = []
        mean_data = []
        for i in range(len(self.devices)):
            fifo_name = '%s%i' %(self.devices[i].properties['Type'],self.devices[i].properties['Input']['Hardware']['PortID'])
            data = copy.copy(np.array([_session.adw.get_fifo(self.fifo.properties[fifo_name])]))
            calibration = self.devices[i].properties['Input']['Calibration']
            data = np.array((data-calibration['Offset'])/calibration['Slope'])
            if self.devices[i].properties['Type']=='Counter':
                data /= self.timeDelay
                
            final_data.append(data)
            mean_data.append(np.mean(data))
        self.emit( QtCore.SIGNAL('TimeTraces'), final_data)
        self.emit( QtCore.SIGNAL('MeanData'), mean_data) # For updating values in an external dialog

    def updateTimes(self,data):
        """ Updates the plots of the variances.
        """
        #Check the sizes of the variances
        var = copy.copy(data)
        for i in range(len(var)):
            xdata = np.arange(len(var[i][0]))*self.timeDelay
            old_data = self.data[i]
            old_t = self.t[i]
            self.t[i] = np.append(self.t[i],xdata+max(self.t[i])+self.timeDelay)
            self.data[i] = np.append(self.data[i],var[i])
            limit = _session.timetrace_time/self.timeDelay
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
                _session.adw.adw.Set_Processdelay(10,self.delay)
                _session.adw.start(10)
                self.ctimer.start(_session.monitor_timeresol*1.2)
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
        
        # Saves the data to binary format. Sometimes (not sure why) the ascii data is not being save properly... 
        # Only what would appear on the screen when printing self.data.
        try:
            np.save("%s%s" %(savedir,filename[:-4]), np.array(self.data))
        except:
            print('Error with Save')
            print(sys.exc_info()[0])
            
        print('Data saved in %s'%(savedir+filename) )
        return
        
    def updateParameters(self):
        """ Updates the relevant parameters for the monitor timetrace. 
        """
        if self.timeDelay != _session.monitor_timeresol/1000:
            # Calculate new time resolution in ADw cycles.
            self.delay = m.floor(_session.monitor_timeresol/1000/_session.adw.time_low)
            self.timeDelay = _session.monitor_timeresol/1000
            _session.adw.adw.Set_Processdelay(10,self.delay)
        
        
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
        
    def bootAdwin(self):
        """ Boots the ADwin and loads the necessary binary files. 
            It is made a separate function to avoid booting and overriding what was achieved 
            with the SmartScan.
        """
        if _session.adw.adw.Test_Version() != 0: # Not clear if this means the ADwin is booted or not
            _session.adw.boot()
            _session.adw.init_port7()
            print('Booting the ADwin...')

        _session.adw.load('lib/adbasic/init_adwin.T98')
        _session.adw.start(8)
        _session.adw.wait(8)
        _session.adw.load('lib/adbasic/monitor.T90')
        _session.adw.load('lib/adbasic/adwin.T99')

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
    mon = Monitor()
    mon.show()
    sys.exit(app.exec_())
