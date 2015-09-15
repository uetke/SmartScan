import sys
from PyQt4 import QtCore, QtGui
#from pyqtgraph.Qt import QtCore, QtGui

class win1(QtGui.QMainWindow):
    def __init__(self):
        super(win1, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.widget1 = wid1()
        self.setCentralWidget(self.widget1)
        self.windows = []
        
        
        self.widget1.btn.clicked[bool].connect(self.show_win)
        
    def show_win(self):
        self.windows.append(win2())
        self.windows[-1].show()
        
        
class wid1(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.layout = QtGui.QGridLayout(self)
        self.btn = QtGui.QPushButton('Test',self)
        self.layout.addWidget(self.btn, 1, 1)
        
class win2(QtGui.QMainWindow):
    def __init__(self):
        super(win2, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.widget1 = wid1()
        self.setCentralWidget(self.widget1)
        
        #self.window2 = win1()
        
        #self.widget1.btn.clicked[bool].connect(self.show_win)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        
    def show_win(self):
        self.window2.show()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    test = win1()
    test.show()
    app.exec_()