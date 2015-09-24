'''
Created on 18 sep. 2015

@author: carattino
'''
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


class PowerSpectra(QtGui.QMainWindow):
    """ Main window for holding the Power Spectra widget. 
    """
    def __init__(self,parent=None):
        super(PowerSpectra,self).__init__()
        
        # Layout
        self.setWindowTitle('Power Spectra')
        self.setGeometry(30,30,450,900)
        self.timetraces = PowerSpectraWidget()
        self.setCentralWidget(self.timetraces)
        
        # Initialize the parameters
        self.time = _session.time
        self.accuracy = _session.accuracy
class PowerSpectraWidget(QtGui.QWidget):
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

        _session.runs = True # Continuous runs
         
        self.workThread = workThread()
        self.connect(self.workThread, QtCore.SIGNAL("QPD"), self.updateGUI )
        self.connect(self.workThread,  QtCore.SIGNAL('Stop_Tr'), self.stop_tr)
        self.setStatusTip('Running...')
        self.is_running = False # Status of the thread
         
    def stop_tr(self):
        """ Emmits a signal for stopping the TR.
        """
        self.emit(QtCore.SIGNAL('Stop_Tr'))
    
    def stop_acq(self):
        """ Stops the continuous runs.
        """
        _session.runs = False
        
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
        self.curvex.setData(self.freqs[2:],values[1,1:])
        self.curvey.setData(self.freqs[2:],values[0,1:])
        self.curvez.setData(self.freqs[2:],values[2,1:])
        self.curved.setData(self.freqs[2:],values[3,1:])
         
        if _session.runs: # If the continuous runs is activated, then refresh.
            self.update()
         
             
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

if __name__ == '__main__':
    pass