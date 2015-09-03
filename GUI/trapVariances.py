from pyqtgraph.Qt import QtGui

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