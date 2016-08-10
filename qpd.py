from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
from time import sleep
import os
from datetime import datetime

from devices.powermeter1830c import powermeter1830c as pp
from lib.adq_mod import adq
#from lib.xml2dict import variables

#par=VARIABLES['par']
#fpar=VARIABLES['fpar']
#data=VARIABLES['data']
#fifo=VARIABLES['fifo']

time = 5 # 1 Second acquisition
accuracy = .00005 # Accuracy in seconds

class Variances(QtGui.QWidget):
    """ Class for showing the variances in the timetraces from the QPD. 
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setWindowTitle('Variances of the QPD')
        self.setGeometry(30,30,450,900)
        self.layout = QtGui.QGridLayout(self)
        
        # Initial variances data
        self.var = np.zeros([3,250])
        x = np.arange(np.size(self.var,axis=1))
        # Variances
        vx = pg.PlotWidget()
        vy = pg.PlotWidget()
        vz = pg.PlotWidget()
        
        self.varx = vx.plot(x,self.var[0,:],pen='y')
        vx.setLabel('left', "Variance", units='U.A.')
        vx.setLabel('bottom', "time", units='Steps')
        
        self.vary = vy.plot(x,self.var[1,:],pen='y')
        vy.setLabel('left', "Variance", units='U.A.')
        vy.setLabel('bottom', "time", units='Steps')
        
        self.varz = vz.plot(x,self.var[2,:],pen='y')
        vz.setLabel('left', "Variance", units='U.A.')
        vz.setLabel('bottom', "time", units='Steps')
        
        self.layout.addWidget(vx, 0, 0)
        self.layout.addWidget(vy, 1, 0)
        self.layout.addWidget(vz, 2, 0)
        
        
        
    def updateVariances(self,variances):
        """ Updates the plots of the variances. 
        """
        # Check the sizes of the variances
        s = np.size(variances, 1)
        self.var = np.roll(self.var,-s,axis=1)
        self.var[:,-s:] = variances
        x = np.arange(np.size(self.var,axis=1))
        self.varx.setData(x,self.var[0,:])
        self.vary.setData(x,self.var[1,:])
        self.varz.setData(x,self.var[2,:])
        


class Power_Spectra(QtGui.QWidget):
    """ Class for starting the needed windows and updating the screen. 
    """
    def __init__(self,time,accuracy,adw,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.setWindowTitle('QPD Power Spectrum')
        
        self.layout = QtGui.QGridLayout(self)
        
        # Power Spectrum
        px = pg.PlotWidget()
        py = pg.PlotWidget()
        pz = pg.PlotWidget()
        
        # Mean Values
        qpdx = QtGui.QLCDNumber()
        qpdx.display(123.5)

        qpdy = QtGui.QLCDNumber()
        qpdy.display(124.5)

        qpdz = QtGui.QLCDNumber()
        qpdz.display(125.6)
        
        
        self.layout.addWidget(px, 0, 0,3,1)
        self.layout.addWidget(py, 0, 1,3,1)
        self.layout.addWidget(pz, 3, 0,3,1)
        self.layout.addWidget(qpdx,3,1)
        self.layout.addWidget(qpdy,4,1)
        self.layout.addWidget(qpdz,5,1)
        
        self.time = time
        self.accuracy = accuracy
        num_points = int(time/accuracy)
        freqs = np.fft.rfftfreq(num_points, accuracy)
        initial_data = np.random.normal(size=(num_points))
        initial_ps = np.abs(np.fft.rfft(initial_data))**2
        

        self.curvex = px.plot(freqs,initial_ps,pen='y')
        px.setLabel('left', "Power Spectrum", units='U.A.')
        px.setLabel('bottom', "Frequency", units='Hz')
        px.setLogMode(x=True, y=True)
        
        
        self.curvey = py.plot(freqs,initial_ps,pen='y')
        py.setLabel('left', "Power Spectrum", units='U.A.')
        py.setLabel('bottom', "Frequency", units='Hz')
        py.setLogMode(x=True, y=True)
        
        self.curvez = pz.plot(freqs,initial_ps,pen='y')
        pz.setLabel('left', "Power Spectrum", units='U.A.')
        pz.setLabel('bottom', "Frequency", units='Hz')
        pz.setLogMode(x=True, y=True)
        
        px.enableAutoRange('xy', True)  
        py.enableAutoRange('xy', True)  
        pz.enableAutoRange('xy', True)  
        
        
        self.freqs = freqs
        self.qpdx = qpdx
        self.qpdy = qpdy
        self.qpdz = qpdz
        self.num_points = num_points
        
        
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S), self), QtCore.SIGNAL('activated()'), self.fileSave)
                
        self.pmeter = pp(0)
        self.pmeter.initialize()
        self.pmeter.wavelength = 1064
        self.pmeter.attenuator = True
        self.pmeter.filter = 'Medium' 
        self.pmeter.go = True
        self.pmeter.units = 'Watts' 
        
        self.variances_gui = Variances()
        self.variances_gui.show()
        self.continuous_runs = True
        
        self.workThread = workThread(self.time,self.accuracy,adw)
        self.connect( self.workThread, QtCore.SIGNAL("QPD"), self.updateGUI )
        
        self.setStatusTip('Running...')
        self.is_running = True
        self.workThread.start()
        

        
    def update(self):
        """ Connects the signals of the working Thread with the appropriate functions in the main Class. 
        """
        self.setStatusTip('Running...')
        if self.is_running == False:
            self.is_running = True
            self.workThread.start()
        else:
            print('Try to re-run')
    
    def updateGUI(self,frequencies,values,data):
        """Updates the curves in the screen and the mean values. 
        """
        self.setStatusTip('Stopped...')
        self.is_running = False
        self.data = data
        self.freqs = frequencies
        self.curvey.setData(self.freqs[1:],values[1,1:])
        self.curvex.setData(self.freqs[1:],values[0,1:])
        self.curvez.setData(self.freqs[1:],values[2,1:])
        self.qpdx.display('%5.1f'%(values[3,0]) )
        self.qpdy.display('%5.1f'%(values[3,1]) )
        self.qpdz.display('%5.1f'%(values[3,2]) )
        box_size = int(.1/self.accuracy)
        num_variances = int(self.time*10)
        variances = np.zeros([3,num_variances])
        for i in range(num_variances):
            variances[:,i] = np.var(data[:,i*box_size:(i+1)*box_size], axis=1)
        self.variances_gui.updateVariances(variances)
        
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
        #try:
        #    power = self.pmeter.data*1000000
        #except:
        #    power = 0
        power = 0
        np.savetxt("%s%s"%(savedir,filename_params), [self.time, self.accuracy, power], header=header,fmt='%s',delimiter=',')
        print('Data saved in %s and configuration data in %s'%(savedir+filename,filename_params) )
        return
    
    def exit_safe(self):
        """ Exits waiting for the Working Thread to finish running. 
        """
        self.workThread.terminate()
        app.quit()

class workThread(QtCore.QThread):
    """ This is the class that will update the values from the QPD. Since it is an expensive task, it will be threaded. 
    """
    def __init__(self,time,accuracy,adw):
        QtCore.QThread.__init__(self)
        self.time = time
        self.accuracy = accuracy
        self.adw = adw
        
    def __del__(self):
        self.wait()
    
    def updateTimes(self,time,accuracy):
        """ Updates the time and the accuracy of the acquisitions. 
        """
        self.time = time
        self.accuracy = accuracy
    
    def run(self):
        """ Triggers the ADwin to acquire a new set of data. It is a time consuming task. 
        """
        num_points = int(self.time/self.accuracy)
        self.freqs = np.fft.rfftfreq(num_points, self.accuracy)
        datax, datay, dataz = self.adw.get_QPD(self.time,self.accuracy)
        #datax = np.random.rand(int(num_points))
        #datay = np.random.rand(int(num_points))
        #dataz = np.random.rand(int(num_points))
        #sleep(2)
        
        pwrx = np.abs(np.fft.rfft(datax))**2
        pwry = np.abs(np.fft.rfft(datay))**2
        pwrz = np.abs(np.fft.rfft(dataz))**2
        
        data = np.zeros([4,len(pwrx)])
        values = np.zeros([3,len(datax)])
        data[0,:] = pwrx
        data[1,:] = pwry
        data[2,:] = pwrz
        data[3,0] = np.mean(datax)
        data[3,1] = np.mean(datay)
        data[3,2] = np.mean(dataz)
        values[0,:] = datax
        values[1,:] = datay
        values[2,:] = dataz
        
        self.emit( QtCore.SIGNAL('QPD'), self.freqs, data, values )
        return 
    

class ConfigureTimes(QtGui.QWidget):
    """ Simple class to change the values for the acquisition times. 
    """
    def __init__(self,tt,acc,parent=None):
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
        runs = self.contin_runs.isChecked()
        self.emit( QtCore.SIGNAL('Times'), new_time, new_accuracy, runs)

        

class MainWindow(QtGui.QMainWindow):
    """ Window that will contain the Power Spectrum widget and some configuration options. 
    """
    def __init__(self,time,accuracy):
        super(MainWindow,self).__init__()
        self.initUI(time,accuracy)
        
    def initUI(self,time,accuracy):
        adw = adq()
        adw.load('lib/adbasic/qpd.T98')
        
        self.power_spectra = Power_Spectra(time,accuracy,adw)
        self.conf_times = ConfigureTimes(time,accuracy)
        self.setCentralWidget(self.power_spectra)
        self.setGeometry(450,30,900,900)
        self.connect(self.conf_times,  QtCore.SIGNAL("Times"),self.power_spectra.updateTimes)
        QtCore.QObject.connect(self.conf_times.run_button, QtCore.SIGNAL('clicked()'),self.power_spectra.update)
        
        saveAction = QtGui.QAction(QtGui.QIcon('floppy-icon.png'),'Save',self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save the displayed data')
        saveAction.triggered.connect(self.power_spectra.fileSave)
        
        exitAction = QtGui.QAction(QtGui.QIcon('Signal-stop-icon.png'),'Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit the program in a safe way')
        exitAction.triggered.connect(self.power_spectra.exit_safe)
        
        configureTimes = QtGui.QAction(QtGui.QIcon('pinion-icon.png'),'Configure',self)
        configureTimes.setShortcut('Ctrl+T')
        configureTimes.setStatusTip('Configure the acquisition times')
        configureTimes.triggered.connect(self.conf_times.show)
        
        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)
        confgMenu = menubar.addMenu('&Configure')
        confgMenu.addAction(configureTimes)
        
    def configure_times(self,time,accuracy):
        """ Configures the times in the power spectra acquisition Widget. 
        """
        
        self.power_spectra.updateTimes(time, accuracy)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    test = MainWindow(time,accuracy)
    test.show()
    app.exec_()