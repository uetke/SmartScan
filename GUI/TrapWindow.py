import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import sys
import pyqtgraph as pg
import os 
from datetime import datetime
import _session

from lib.xml2dict import variables
from matplotlib.backend_bases import CloseEvent

from devices import powermeter1830c as pp

class MainWindow(QtGui.QMainWindow):
    """ Window that will contain the Power Spectrum widget and some configuration options. 
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
        QtCore.QObject.connect(self.monitor_values, QtCore.SIGNAL('TimeTraces'),self.timetraces.updateTimes)
        
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
#         exitAction.triggered.connect(self.exit_safe)
        
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

        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)
        fileMenu.addAction(runMonitor)
        fileMenu.addAction(stopMonitor)
        confgMenu = menubar.addMenu('&Configure')
        confgMenu.addAction(configureTimes)
        confgMenu.addAction(showTimetraces)
        confgMenu.addAction(acquireTimetrace)
        
    def closeEvent(self, event):
        _session.adw.stop(10)
        event.accept()
#         
#     def configure_times(self,time,accuracy):
#         """ Configures the times in the power spectra acquisition Widget. 
#         """
#         
#         self.power_spectra.updateTimes(time, accuracy)


class TimeTraces(QtGui.QWidget):
    """ Class for showing the variances in the timetraces from the QPD. 
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setWindowTitle('Timetraces')
        self.setGeometry(30,30,450,900)
        self.layout = QtGui.QGridLayout(self)
         
        # Initial timetrace data
        self.var = np.zeros([4,250])
        x = np.arange(np.size(self.var,axis=1))
        # Timetraces
        qpdx = pg.PlotWidget()
        qpdy = pg.PlotWidget()
        diff = pg.PlotWidget()
        apd1 = pg.PlotWidget()
         
        self.varx = qpdx.plot(x,self.var[0,:],pen='y')
        qpdx.setLabel('left', "QPD X", units='U.A.')
        qpdx.setLabel('bottom', "time", units='Steps')
         
        self.vary = qpdy.plot(x,self.var[1,:],pen='y')
        qpdy.setLabel('left', "QPD Y", units='U.A.')
        qpdy.setLabel('bottom', "time", units='Steps')
         
        self.vard = diff.plot(x,self.var[2,:],pen='y')
        diff.setLabel('left', "Diff", units='U.A.')
        diff.setLabel('bottom', "time", units='Steps')
        
        self.vara = apd1.plot(x,self.var[3,:],pen='y')
        apd1.setLabel('left','APD', units = 'CPS')
        apd1.setLabel('bottom','time',units='Steps')
         
        self.layout.addWidget(qpdx, 0, 0)
        self.layout.addWidget(qpdy, 0, 1)
        self.layout.addWidget(diff, 1, 0)
        self.layout.addWidget(apd1, 1, 1)
         
    def updateTimes(self,variances):
        """ Updates the plots of the variances. 
        """
        #Check the sizes of the variances
        for i in range(len(variances)):
            s = np.size(variances[i])
            self.var[i,:] = np.roll(self.var[i],-s,axis=0)
            self.var[i,-s:] = variances[i]
        
        x = np.arange(np.size(self.var,axis=1))
        self.varx.setData(x,self.var[0,:])
        self.vary.setData(x,self.var[1,:])
        self.vard.setData(x,self.var[2,:])
        self.vara.setData(x,self.var[3,:])

class Power_Spectra(QtGui.QWidget):
    """ Class for starting the needed windows and updating the screen. 
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
         
        self.setWindowTitle('QPD Power Spectrum')
         
        self.layout = QtGui.QGridLayout(self)
         
        """ Power Spectrum """
        px = pg.PlotWidget()
        py = pg.PlotWidget()
        pz = pg.PlotWidget()
        
        """ Balanced PD"""
        diff = pg.PlotWidget()

        self.layout.addWidget(px, 0, 0)
        self.layout.addWidget(py, 0, 1)
        self.layout.addWidget(pz, 1, 0)
        self.layout.addWidget(diff,1,1)
         
        self.time = _session.time
        self.accuracy = _session.accuracy
        
        num_points = int(self.time/self.accuracy)
        freqs = np.fft.rfftfreq(num_points, self.accuracy)
        initial_data = np.random.normal(size=(num_points))
        initial_ps = np.abs(np.fft.rfft(initial_data))**2
                  
        self.freqs = freqs
        self.num_points = num_points
 
        self.curvex = px.plot(freqs,initial_ps,pen='y')
        px.setLabel('left', "Power Spectrum X", units='U.A.')
        px.setLabel('bottom', "Frequency", units='Hz')
        px.setLogMode(x=True, y=True)
         
         
        self.curvey = py.plot(freqs,initial_ps,pen='y')
        py.setLabel('left', "Power Spectrum Y", units='U.A.')
        py.setLabel('bottom', "Frequency", units='Hz')
        py.setLogMode(x=True, y=True)
         
        self.curvez = pz.plot(freqs,initial_ps,pen='y')
        pz.setLabel('left', "Power Spectrum Z", units='U.A.')
        pz.setLabel('bottom', "Frequency", units='Hz')
        pz.setLogMode(x=True, y=True)
        
        self.curved = diff.plot(freqs,initial_ps,pen='y')
        diff.setLabel('left', "Power Spectrum Diff", units='U.A.')
        diff.setLabel('bottom', "Frequency", units='Hz')
        diff.setLogMode(x=True, y=True)
         
        px.enableAutoRange('xy', True)  
        py.enableAutoRange('xy', True)  
        pz.enableAutoRange('xy', True)  
        diff.enableAutoRange('xy',True)
         
         
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S), self), QtCore.SIGNAL('activated()'), self.fileSave)
                 
#         self.pmeter = pp(0)
#         self.pmeter.initialize()
#         self.pmeter.wavelength = 1064
#         self.pmeter.attenuator = True
#         self.pmeter.filter = 'Medium' 
#         self.pmeter.go = True
#         self.pmeter.units = 'Watts' 

        self.continuous_runs = True
         
        self.workThread = workThread()
        self.connect(self.workThread, QtCore.SIGNAL("QPD"), self.updateGUI )
         
        self.setStatusTip('Running...')
        self.is_running = False
         
 
    def update(self):
        """ Connects the signals of the working Thread with the appropriate functions in the main Class. 
        """
        self.setStatusTip('Running...')
        if self.is_running == False:
            self.is_running = True
            self.workThread.start()
        else:
            print('Try to re-run')
     
    def updateGUI(self,frequencies,data,values):
        """Updates the curves in the screen and the mean values. 
        """
        self.setStatusTip('Stopped...')
        self.is_running = False
        self.data = data
        self.freqs = frequencies
        self.curvey.setData(self.freqs[1:],values[1,1:])
        self.curvex.setData(self.freqs[1:],values[0,1:])
        self.curvez.setData(self.freqs[1:],values[2,1:])
        self.curved.setData(self.freqs[1:],values[3,1:])
         
        if self.continuous_runs: # If the continuous runs is activated, then refresh.
            self.update()
         
         
    def updateTimes(self,time,accuracy,runs):
        """ Updates the time and the accuracy for the plots. 
        """
        self.time = time
        self.accuracy = accuracy
        self.continuous_runs = runs
        self.workThread.updateTimes(time, accuracy)
             
    def fileSave(self):
        """Saves the files to a specified folder. 
        """
        name = 'QPD_Data'
        savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        i=1
        filename = name
        while os.path.exists(savedir+filename+".dat"):
            filename = '%s_%s' %(name,i)
            i += 1
        filename_params = filename +'_config'
        filename = filename+".dat"
        np.savetxt("%s%s" %(savedir,filename), self.data,fmt='%s', delimiter=",")
        filename_params = filename_params+".dat"
        header = "Length, Integration Time, 1064 power"
#         try:
#             power = self.pmeter.data*1000000
#         except:
#             power = 0
        power = 0
        np.savetxt("%s%s"%(savedir,filename_params), [self.time, self.accuracy, power], header=header,fmt='%s',delimiter=',')
        print('Data saved in %s and configuration data in %s'%(savedir+filename,filename_params) )
        return
     
    def exit_safe(self):
        """ Exits waiting for the Working Thread to finish running. 
        """
        self.workThread.terminate()
        app.quit()
        
class ConfigureTimes(QtGui.QWidget):
    """ Simple class to change the values for the acquisition times. 
    """
    def __init__(self,parent=None):
        tt = _session.time 
        acc = _session.accuracy 
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Configure the times')
        self.setGeometry(30,30,100,100)
        self.layout = QtGui.QGridLayout(self)
         
        self.time_label = QtGui.QLabel(self)
        self.time_label.setText('Time (s): ')
        self.time = QtGui.QLineEdit(self)
        self.time.setText(str(tt))
        self.accuracy_label = QtGui.QLabel(self)
        self.accuracy_label.setText('Accuracy (ms): ')
        self.accuracy = QtGui.QLineEdit(self)
        self.accuracy.setText(str(acc*1000))
         
        self.contin_runs = QtGui.QCheckBox('Continuous runs', self)
        self.contin_runs.setChecked(True)
         
        self.apply_button = QtGui.QPushButton('Apply', self)
        self.apply_button.clicked[bool].connect(self.SetTimes)
         
        self.run_button = QtGui.QPushButton('Run', self)
 
        self.layout.addWidget(self.time_label,0,0)
        self.layout.addWidget(self.time,0,1)
        self.layout.addWidget(self.accuracy_label,1,0)
        self.layout.addWidget(self.accuracy,1,1)
        self.layout.addWidget(self.contin_runs,2,0)
        self.layout.addWidget(self.apply_button,3,0,1,2)
        self.layout.addWidget(self.run_button,4,0,1,2)
         
    def SetTimes(self):
        new_time = float(self.time.text())
        new_accuracy = float(self.accuracy.text())/1000
        _session.time = new_time
        _session.accuracy = new_accuracy
        _session.runs = self.contin_runs.isChecked()
        self.emit( QtCore.SIGNAL('Times'), new_time, new_accuracy, runs)

class monitor_values(QtGui.QWidget):
    """ Class for monitoring the values of given devices. 
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        # Starts the monitor routine in the ADwin
        global _session
        self.adw = _session.adw       
        self.detector = _session.devices

        self.layout = QtGui.QGridLayout(self)
        
        # Mean Values
        # QPD
        qpdx = QtGui.QLCDNumber()
        qpdx.display(123.1)

        qpdy = QtGui.QLCDNumber()
        qpdy.display(124.2)

        qpdz = QtGui.QLCDNumber()
        qpdz.display(125.3)
        
        # Balanced Photodetector 
        monitor1 = QtGui.QLCDNumber()
        monitor1.display(125.4)
        
        monitor2 = QtGui.QLCDNumber()
        monitor2.display(125.5)
        
        diff = QtGui.QLCDNumber()
        diff.display(125.6)
        
        self.layout.addWidget(monitor1, 1, 0)
        self.layout.addWidget(monitor2, 2, 0)
        self.layout.addWidget(diff, 3, 0)
        self.layout.addWidget(qpdx,1,1)
        self.layout.addWidget(qpdy,2,1)
        self.layout.addWidget(qpdz,3,1)
        
        self.qpdx = qpdx
        self.qpdy = qpdy
        self.qpdz = qpdz
        self.monitor1 = monitor1
        self.monitor2 = monitor2
        self.diff = diff
        
        # Starts the timer for the updates.
        self.ctimer = QtCore.QTimer()
        self.running = False
        
        QtCore.QObject.connect(self.ctimer,QtCore.SIGNAL("timeout()"),self.updateMeans)
        
        self.fifo=variables('Fifo')
        self.fifo_name = ''
        
    def start_timer(self):
        """ Starts the timer with a predefined update interval. 
        """
        if not self.running:
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
        

    def updateMeans(self):
        final_data = []
        for i in range(len(self.detector)):
            self.fifo_name = '%s%i' %(self.detector[i].properties['Type'],self.detector[i].properties['Input']['Hardware']['PortID'])
            data = np.array([self.adw.get_fifo(self.fifo.properties[self.fifo_name])])
            calibration = self.detector[i].properties['Input']['Calibration']
            data = (data-calibration['Offset'])/calibration['Slope']
            
            #final_data = np.vstack((xdata,data))
            name = self.detector[i].properties['Name']
            if name == "Monitor +":
                self.monitor1.display(np.mean(data))
            elif name == "Monitor -":
                self.monitor2.display(np.mean(data))
            elif name == "Diff":
                self.diff.display(np.mean(data))
                final_data.append(data)
            elif name == "QPD X":
                self.qpdx.display(np.mean(data))
                final_data.append(data)
            elif name == "QPD Y":
                self.qpdy.display(np.mean(data))
                final_data.append(data)
            elif name == "QPD Z":
                self.qpdz.display(np.mean(data))
            elif name == "APD 1":
                final_data.append(data)
        self.emit( QtCore.SIGNAL('TimeTraces'), final_data)
                
 
class workThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.time = _session.time
        self.accuracy = _session.accuracy
        self.adw = _session.adw

    def __del__(self):
        self.wait()
     
#     def updateTimes(self,time,accuracy):
#         """ Updates the time and the accuracy of the acquisitions. 
#         """
#         self.time = time
#         _session['time'] = time
#         self.accuracy = accuracy
#         _session['accuracy'] = accuracy
     
    def run(self):
        """ Triggers the ADwin to acquire a new set of data. It is a time consuming task. 
        """
        num_points = int(_session.time/_session.accuracy)
        freqs = np.fft.rfftfreq(num_points, _session.accuracy)           
        """ Need to stop the monitor? 
            If the monitor changes the position of the multiplexor, then it will 
            alter the timing between the measurements. 
        """
        try:
            self.adw.stop(10)
        except:
            print('Process 10 was not running')
        
        dev = _session.devices[0:4]
        data_adw = self.adw.get_QPD(dev,_session.time,_session.accuracy)
        #datax = np.random.rand(int(num_points))
        #datay = np.random.rand(int(num_points))
        #dataz = np.random.rand(int(num_points))
        #sleep(2)
         
        """ Have to assume a particular order of the devices, i.e. QPDx->QPDy->QPDz->->Diff """
         
        pwrx = np.abs(np.fft.rfft(data_adw[0]))**2
        pwry = np.abs(np.fft.rfft(data_adw[1]))**2
        pwrz = np.abs(np.fft.rfft(data_adw[2]))**2
        diff = np.abs(np.fft.rfft(data_adw[3]))**2
        
        values = np.zeros([5,len(pwrx)])
        data = np.zeros([4,len(data_adw[0])])
        values[0,:] = pwrx
        values[1,:] = pwry
        values[2,:] = pwrz
        values[3,:] = diff
        values[4,0] = np.mean(data_adw[0])
        values[4,1] = np.mean(data_adw[1])
        values[4,2] = np.mean(data_adw[2])
        values[4,3] = np.mean(data_adw[3])
        data[0,:] = data_adw[0]
        data[1,:] = data_adw[1]
        data[2,:] = data_adw[2]
        data[3,:] = data_adw[3]
         
        self.emit( QtCore.SIGNAL('QPD'), freqs, data, values)
        return 


if __name__ == "__main__":   
    from lib.xml2dict import device
    _session.time = 1
    _session.accuracy = 0.05  
    
    if _session.adw.adw.Test_Version() != 1: # Not clear if this means the ADwin is booted or not
        _session.adw.boot()
        _session.adw.init_port7()
        print('Booting the ADwin...')
            
    _session.adw.load('lib/adbasic/init_adwin.T98')
    _session.adw.start(8)
    _session.adw.wait(8)
    _session.adw.load('lib/adbasic/monitor.T90')
    _session.adw.load('lib/adbasic/adwin.T99')

    qpdx = device('QPD X')
    qpdy = device('QPD Y')
    qpdz = device('QPD Z')
    diffx = device('Monitor +')
    diffy = device('Monitor -')
    monitor = device('Diff')
    apd1 = device('APD 1')  
    
    devices = [qpdx,qpdy,qpdz,diffx,diffy,monitor,apd1]
    _session.devices = devices
    app = QtGui.QApplication(sys.argv)
    test = MainWindow()
    test.show()
    app.exec_()