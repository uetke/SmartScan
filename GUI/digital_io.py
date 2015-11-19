import sys
from PyQt4 import QtCore, QtGui, QtSvg
from PyQt4.QtWebKit import QGraphicsWebView
import _session

class digitalWindow(QtGui.QWidget):
    """ Class for showing the status of the digital in and outs of the ADwin 
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setWindowTitle('Timetraces')
        self.setGeometry(30,30,450,900)
        self.layout = QtGui.QGridLayout(self)
        
    def updateCircles(self):
        """ Updates the color of the circles.
        """
        
    def trigger(self,port):
        """ Generates a square function on the selected port.
        """

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    window.setGeometry(50, 50, 400, 200)
    pic = QtGui.QLabel(window)
    pic.setGeometry(50, 50, 400, 100)
    #use full ABSOLUTE path to the image, not relative
    pic.setPixmap(QtGui.QPixmap("D:\\Programs\\scan_develop\\scan-2.0\\GUI\\Icons\\green_circle.png"))
    
    window.show()
    sys.exit(app.exec_())