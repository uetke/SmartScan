from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import time 
import sys

class MyApp(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(30,30,900,900)
        self.layout = QtGui.QGridLayout(self)
        time = 1
        accuracy = 0.0005
        px = pg.PlotWidget()
        py = pg.PlotWidget()
        pz = pg.PlotWidget()
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
        
        self.layout.addWidget(px, 0, 0)
        self.layout.addWidget(py, 1, 0)
        self.layout.addWidget(pz, 0, 1)
        
        self.layout = QtGui.QGridLayout(self)
        
        self.testButton = QtGui.QPushButton("test")
        self.plot = pg.PlotWidget()
        self.connect(self.testButton, QtCore.SIGNAL("released()"), self.test)
        self.listwidget = QtGui.QListWidget(self)
        
        self.layout.addWidget(self.testButton)
        self.layout.addWidget(self.listwidget)
        
 
    def add(self, text, num):
        """ Add item to list widget """
        print("Add: " + text + str(num))
        self.listwidget.addItem(text+str(num))
        self.listwidget.sortItems()
 
    def addBatch(self,text="test",iters=6,delay=0.3):
        """ Add several items to list widget """
        for i in range(iters):
            time.sleep(delay) # artificial time delay
            self.add(text+" ",str(i))
 
    def test(self):
        self.listwidget.clear()
        # adding in main application: locks ui
        self.addBatch("_non_thread",iters=6,delay=0.3)
        
        # adding by emitting signal in different thread
        self.workThread = WorkThread('test')
        self.connect( self.workThread, QtCore.SIGNAL("Finish"), self.add )
        self.workThread.start()
  
class WorkThread(QtCore.QThread,QtGui.QWidget):
    def __init__(self,text):
        QtCore.QThread.__init__(self)
        self.text = text
    def __del__(self):
        self.wait()
    
    def run(self):
        for i in range(6):
            time.sleep(0.3) # artificial time delay
            self.emit( QtCore.SIGNAL('Finish'), "from work thread ", i )
        return
 
 
if __name__ == "__main__":  
    # run
    app = QtGui.QApplication(sys.argv)
    test = MyApp()
    test.show()
    app.exec_()