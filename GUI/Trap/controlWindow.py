from pyqtgraph.Qt import QtCore, QtGui
import sys

class controlWindow(QtGui.QWidget):
    """ Simple class to change the position of the piezo stage.
    """
    def __init__(self,_session=None,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Move the piezo')
        self.setGeometry(30,30,100,100)
        self.layout = QtGui.QGridLayout(self)
        
        self.x_label = QtGui.QLabel(self)
        self.x_label.setText('X Piezo (um)')
        self.x_increase = QtGui.QLineEdit(self)
        self.x_increase.setText(str(0.1))
        self.x_plus = QtGui.QPushButton('+', self)
        self.x_plus.setObjectName('x+')
        self.x_minus = QtGui.QPushButton('-', self)
        self.x_minus.setObjectName('x-')
        
        self.y_label = QtGui.QLabel(self)
        self.y_label.setText('Y Piezo (um)')
        self.y_increase = QtGui.QLineEdit(self)
        self.y_increase.setText(str(0.1))
        self.y_plus = QtGui.QPushButton('+', self)
        self.y_minus = QtGui.QPushButton('-', self)
        self.y_plus.setObjectName('y+')
        self.y_minus.setObjectName('y-')
        
        self.z_label = QtGui.QLabel(self)
        self.z_label.setText('Y Piezo (um)')
        self.z_increase = QtGui.QLineEdit(self)
        self.z_increase.setText(str(0.1))
        self.z_plus = QtGui.QPushButton('+', self)
        self.z_minus = QtGui.QPushButton('-', self)
        self.z_plus.setObjectName('z+')
        self.z_minus.setObjectName('z-')
        
        self.layout.addWidget(self.x_label,0,0)
        self.layout.addWidget(self.x_increase,0,1)
        self.layout.addWidget(self.x_plus,0,2)
        self.layout.addWidget(self.x_minus,0,3)
        
        self.layout.addWidget(self.y_label,1,0)
        self.layout.addWidget(self.y_increase,1,1)
        self.layout.addWidget(self.y_plus,1,2)
        self.layout.addWidget(self.y_minus,1,3)
        
        self.layout.addWidget(self.z_label,2,0)
        self.layout.addWidget(self.z_increase,2,1)
        self.layout.addWidget(self.z_plus,2,2)
        self.layout.addWidget(self.z_minus,2,3)
        
        
        QtCore.QObject.connect(self.x_plus, QtCore.SIGNAL('clicked()'), self.buttonClicked)
        QtCore.QObject.connect(self.x_minus, QtCore.SIGNAL('clicked()'), self.buttonClicked)
        QtCore.QObject.connect(self.y_plus, QtCore.SIGNAL('clicked()'), self.buttonClicked)
        QtCore.QObject.connect(self.y_minus, QtCore.SIGNAL('clicked()'), self.buttonClicked)
        QtCore.QObject.connect(self.z_plus, QtCore.SIGNAL('clicked()'), self.buttonClicked)
        QtCore.QObject.connect(self.z_minus, QtCore.SIGNAL('clicked()'), self.buttonClicked)
       
        
    def buttonClicked(self):
        """ Move the piezo stage when a button is pressed.
        """
        sender = self.sender()
        name = sender.objectName()
        
        print(sender.objectName())
                
if __name__ == "__main__":
    """
        Do something.
    """
    app = QtGui.QApplication(sys.argv)
    conWindow = controlWindow()
    conWindow.show()
    app.exec_()
    