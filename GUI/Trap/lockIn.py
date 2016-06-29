'''
Created on 27 jun. 2016
@author: carattino
'''
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import sys
import pyqtgraph as pg
import _session
from PyQt4.Qt import QApplication
import os
from datetime import datetime
import time

class LockIn(QtGui.QMainWindow):
    """ Main window for the APD timetrace.
    """
    def __init__(self,parent=None):
        super(LockIn,self).__init__()

        # Layout
        self.setWindowTitle('Lock-In Timetraces')
        self.setGeometry(30,30,450,900)
        self.timetraces = lockInWidget()
        self.setCentralWidget(self.timetraces)

        # Initialization of the parameters
        num_points = int(_session.lockInTime/_session.lockInAcc)
        x = np.linspace(0, _session.lockInTime, num_points)
        y = np.zeros(num_points)
        self.curveLockIn = self.timetraces.lockIn.plot(x,y)

        self.is_running = False

        self.workThread = LockInThread()
        self.connect(self.workThread, QtCore.SIGNAL('LockIn'),self.updateGUI)
        self.connect(self.workThread,  QtCore.SIGNAL('Stop_Tr'), self.stop_tr)

        self.timetraces.triggerLockIn.clicked[bool].connect(self.start_timetrace)

        exitAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/Signal-stop-icon.png'),'Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit the timetrace monitor in a safe way')
        exitAction.triggered.connect(self.exit_safe)

        saveAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/floppy-icon.png'),'Save',self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Saves the currently displayed data to a file')
        saveAction.triggered.connect(self.fileSave)

        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

    def updateGUI(self,t,c):
        """ Updates the timetrace with the values of t and c.
        """
        self.is_running = False
        self.data = np.c_[t,c]
        self.curveLockIn.setData(t,c)

    def stop_tr(self):
        """ Emmits a signal for stopping the timetraces.
        """
        self.emit(QtCore.SIGNAL('Stop_Tr'))

    def fileSave(self):
        """ Saves the data to a file.
        """
        name = 'LockIn_Data'
        savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        i=1
        filename = name
        while os.path.exists(savedir+filename+".dat"):
            filename = '%s_%s' %(name,i)
            i += 1
        filename_params = filename +'_config.dat'
        filename = filename+".dat"
        header = 'Time (s), Signal (V)'
        np.savetxt("%s%s" %(savedir,filename), self.data,fmt='%s', delimiter=",",header=header)

        header = "Length, Integration Time, 1064 power"
        # try:
        #     power = self.pmeter.data*1000000
        # except:
        #     power = 0
        power = 0
        np.savetxt("%s%s"%(savedir,filename_params), [_session.lockInTime, _session.lockInAcc, power], header=header,fmt='%s',delimiter=',')
        
        # Saves the data to binary format. Sometimes (not sure why) the ascii data is not being save properly... 
        # Only what would appear on the screen when printing self.data.
        try:
            np.save("%s%s" %(savedir,filename[:-4]), self.data)
        except:
            print('Error with Save')
            print(sys.exc_info()[0])
        
        print('Data saved in %s and configuration data in %s'%(savedir+filename,filename_params) )
        
        
        return

    def start_timetrace(self):
        """ Triggers the working thread.
        """
        self.workThread.start()
        self.is_running = True

    def exit_safe(self,event):
        """ Exits the application stopping the working Thread.
        """
        if _session.lockInTime>5:
            # To avoid impatience to force the shutdown.
            print('Waiting for the acquisition to finish.')
            print('It may take up to %s more seconds.'%_session.apdtime)
        self.workThread.terminate()
        self.close()

class lockInWidget(QtGui.QWidget):
    """ Simple class for showing the timetrace of the APD.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Lock In Dedicated Timetrace')
        self.layout = QtGui.QGridLayout(self)

        # APD Timetrace
        lockIn = pg.PlotWidget()
        lockIn.setLabel('left','Lock-In',units='V')
        lockIn.setLabel('bottom','Time',units='s')
        self.lockIn = lockIn

        # Run button for APD Fast timetrace
        self.triggerLockIn = QtGui.QPushButton('Run',self)

        self.layout.addWidget(self.lockIn,0,0,11,12)
        self.layout.addWidget(self.triggerLockIn,12,11,1,1)

class LockInThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        """ Triggers the ADwin for acquiring an APD fast timetrace.
            Returns a list of two arrays, with the arrival time and the number of counts.
        """
        self.emit(QtCore.SIGNAL('Stop_Tr'))
        lockIn = _session.device['lock']
        c,t = _session.adw.get_timetrace_static([lockIn], _session.lockInTime, _session.lockInAcc)
        c = np.reshape(c,-1)
        self.emit(QtCore.SIGNAL('LockIn'),np.array(t),np.array(c))
        return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test = LockIn()
    test.show()
    sys.exit(app.exec_())
