'''
Created on 18 sep. 2015
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

class APD(QtGui.QMainWindow):
    """ Main window for the APD timetrace.
    """
    def __init__(self,parent=None):
        super(APD,self).__init__()

        # Layout
        self.setWindowTitle('APD Timetraces')
        self.setGeometry(30,30,450,900)
        self.timetraces = ApdWidget()
        self.setCentralWidget(self.timetraces)

        # Initialization of the parameters
        num_points = int(_session.apdtime/_session.apdacc)
        x = np.linspace(0, _session.apdtime, num_points)
        y = np.zeros(num_points)
        self.curveapd = self.timetraces.apd.plot(x,y,symbol='o',pen=None)

        self.is_running = False

        self.workThread = APDThread()
        self.connect(self.workThread, QtCore.SIGNAL('APD'),self.updateGUI)
        self.connect(self.workThread,  QtCore.SIGNAL('Stop_Tr'), self.stop_tr)

        self.timetraces.triggerAPD.clicked[bool].connect(self.start_timetrace)

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
        time = t*_session.apdacc
        self.data = [t,c]
        self.curveapd.setData(time,c)

    def stop_tr(self):
        """ Emmits a signal for stopping the timetraces.
        """
        self.emit(QtCore.SIGNAL('Stop_Tr'))

    def fileSave(self):
        """ Saves the data to a file.
        """
        name = 'APD_Data'
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
        np.savetxt("%s%s" %(savedir,filename), self.data,fmt='%s', delimiter=",")

        header = "Length, Integration Time, 1064 power"
        # try:
        #     power = self.pmeter.data*1000000
        # except:
        #     power = 0
        power = 0
        np.savetxt("%s%s"%(savedir,filename_params), [_session.apdtime, _session.apdacc, power], header=header,fmt='%s',delimiter=',')
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
        if _session.apdtime>5:
            # To avoid impatience to force the shutdown.
            print('Waiting for the acquisition to finish.')
            print('It may take up to %s more seconds.'%_session.apdtime)
        self.workThread.terminate()
        self.close()

class ApdWidget(QtGui.QWidget):
    """ Simple class for showing the timetrace of the APD.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('APD Fast Timetrace')
        self.layout = QtGui.QGridLayout(self)

        # APD Timetrace
        apd = pg.PlotWidget()
        apd.setLabel('left','Counts',units='#')
        apd.setLabel('bottom','Time',units='s')
        self.apd = apd

        # Run button for APD Fast timetrace
        self.triggerAPD = QtGui.QPushButton('Run',self)

        self.layout.addWidget(self.apd,0,0,11,12)
        self.layout.addWidget(self.triggerAPD,12,11,1,1)

class APDThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        """ Triggers the ADwin for acquiring an APD fast timetrace.
            Returns a list of two arrays, with the arrival time and the number of counts.
        """
        self.emit(QtCore.SIGNAL('Stop_Tr'))
        apd1 = _session.device['apd1']
        t,c = _session.adw.get_fast_timetrace(apd1, _session.apdtime, _session.apdacc)
        self.emit(QtCore.SIGNAL('APD'),np.array(t),np.array(c))
        return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test = APD()
    test.show()
    sys.exit(app.exec_())
