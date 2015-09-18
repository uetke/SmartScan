'''
Created on 18 sep. 2015

@author: aj carattino
'''
import numpy as np
from pyqtgraph.Qt import QtGui
import sys
import pyqtgraph as pg
from PyQt4.Qt import QApplication

class TimeTraces(QtGui.QMainWindow):
    """ Class for showing the variances in the timetraces from the QPD. 
    """
    def __init__(self,parent=None):
        super(TimeTraces,self).__init__()
        self.setWindowTitle('Timetraces')
        self.setGeometry(30,30,450,900)
        
        self.timetraces = TimetraceWidget()
        self.setCentralWidget(self.timetraces)
        # Initial timetrace data
        self.var = np.zeros([4,250])
        x = np.arange(np.size(self.var,axis=1))

         
        self.varx = self.timetraces.qpdx.plot(x,self.var[0,:],pen='y')
        self.vary = self.timetraces.qpdy.plot(x,self.var[1,:],pen='y')
        self.vard = self.timetraces.diff.plot(x,self.var[2,:],pen='y')
        self.vara = self.timetraces.apd1.plot(x,self.var[3,:],pen='y')
        
        
        exitAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/Signal-stop-icon.png'),'Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit the timetrace monitor in a safe way')
        exitAction.triggered.connect(self.close)
         
        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
         
    def updateTimes(self,variances):
        """ Updates the plots of the variances. 
        """
        #Check the sizes of the variances
        for i in range(len(variances)):
            s = np.size(variances[i])
            self.var[i,:] = np.roll(self.var[i],-s,axis=0)
            self.var[i,-s:] = variances[i]
        
        x = np.arange(np.size(self.var,axis=1))
        self.varx.setData(x,self.var[2,:])
        self.vary.setData(x,self.var[1,:])
        self.vard.setData(x,self.var[0,:])
        self.vara.setData(x,self.var[3,:])

class TimetraceWidget(QtGui.QWidget):
    """ Widget for displaying the Timetraces. 
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        
        # Timetraces
        qpdx = pg.PlotWidget()
        qpdy = pg.PlotWidget()
        diff = pg.PlotWidget()
        apd1 = pg.PlotWidget()
        qpdx.setLabel('left', "QPD X", units='U.A.')
        qpdx.setLabel('bottom', "time", units='Steps')
        qpdy.setLabel('left', "QPD Y", units='U.A.')
        qpdy.setLabel('bottom', "time", units='Steps')
        diff.setLabel('left', "Diff", units='U.A.')
        diff.setLabel('bottom', "time", units='Steps')        
        apd1.setLabel('left','APD', units = 'CPS')
        apd1.setLabel('bottom','time',units='Steps')        
        self.qpdx = qpdx
        self.qpdy = qpdy
        self.diff = diff
        self.apd1 = apd1
        
        # Layout
        self.layout = QtGui.QGridLayout(self)
        self.layout.addWidget(self.qpdx, 0, 0)
        self.layout.addWidget(self.qpdy, 0, 1)
        self.layout.addWidget(self.diff, 1, 0)
        self.layout.addWidget(self.apd1, 1, 1)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mon = TimeTraces()
    mon.show()
    sys.exit(app.exec_())