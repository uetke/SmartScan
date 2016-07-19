""" GUI For controlling the flipper mirrors.
""" 

from devices.flipper import Flipper
from pyqtgraph.Qt import QtGui, QtCore
from PyQt4.Qt import QApplication
import sys

class flippers(QtGui.QMainWindow):
    def __init__(self,parent=None):
        super(flippers,self).__init__()
        self.setWindowTitle('Flippers control')
        self.setGeometry(30,30,100,100)
        self.buttons = flipperWidget()
        self.setCentralWidget(self.buttons)
        
        
        
class flipperWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QGridLayout(self)
        
        self.flipper1 = Flipper(SerialNum=b'37864186')
        self.flipper2 = Flipper(SerialNum=b'37863355')
        self.flipper1.initializeHardwareDevice()
        self.flipper2.initializeHardwareDevice()
        self.flipper1.identify() # Makes the green LED blink
        self.flipper2.identify() # Makes the green LED blink
        
        self.but1_label = QtGui.QLabel(self)
        self.but1_label.setText('Flipper 1: ')
        self.but1 = QtGui.QPushButton('%s'%self.flipper1.getPos(), self)
        self.but2_label = QtGui.QLabel(self)
        self.but2_label.setText('Flipper 2: ')
        self.but2 = QtGui.QPushButton('%s'%self.flipper2.getPos(), self)
        
        
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePos)
        
        self.updatePos()
        
        self.but1.clicked[bool].connect(self.changePos1)
        self.but2.clicked[bool].connect(self.changePos2)
        
        
        self.layout.addWidget(self.but1_label,0,0)
        self.layout.addWidget(self.but1,1,0)
        self.layout.addWidget(self.but2_label,2,0)
        self.layout.addWidget(self.but2,3,0)
        
    def changePos1(self):
        """ Changes the position of the flipper mirror.
        """
        self.flipper1.changePos()
        new_pos = self.flipper1.getPos()
        self.updatePos()
        
    def changePos2(self):
        """ Changes the position of the flipper mirror.
        """
        self.flipper2.changePos()
        self.updatePos()
            
    def updatePos(self):
        """ Gets the current position of the flipper mirrors and updates the text/color
        """
        
         # Flipper 1 position
        self.position = self.flipper1.getPos()
        if self.position == 1:
            self.but1.setStyleSheet('QPushButton {background-color: #db6a64; color: red;}')
        else:
            self.but1.setStyleSheet('QPushButton {background-color: #64db9c; color: green;}')
        self.but1.setText('%s'%self.position)
        
        # Flipper 2 position
        self.position = self.flipper2.getPos()
        if self.position == 1:
            self.but2.setStyleSheet('QPushButton {background-color: #db6a64; color: red;}')
        else:
            self.but2.setStyleSheet('QPushButton {background-color: #64db9c; color: green;}')
        self.but2.setText('%s'%self.position)
        
        self.timer.start(1000)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    flip = flippers()
    flip.show()
    sys.exit(app.exec_())
