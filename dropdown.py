from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from random import randint

"""
class dropdown(QtGui.QWidget):
    def __init__(self, parent=None):
        super(dropdown, self).__init__(parent)
        pushbutton = QtGui.QPushButton('Popup Button')
        menu = QtGui.QMenu()
        menu.addAction('This is Action 1', self.Action1)
        menu.addAction('This is Action 2', self.Action2)
        pushbutton.setMenu(menu)
        #self.setCentralWidget(pushbutton)

    def Action1(self):
        print( 'You selected Action 1')

    def Action2(self):
        print( 'You selected Action 2')
        
"""
class dropdown(QtGui.QWidget):
    def __init__(self,pos,MainWindow):
        QtGui.QWidget.__init__(self)
        #layout = QtGui.QHBoxLayout(self)
        self.button = QtGui.QToolButton(self)
        self.button.setText('Detectors')
        self.button.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.button.setMenu(QtGui.QMenu(self.button))
        self.model = QStandardItemModel()


        self.view = QListView()
        self.action = QtGui.QWidgetAction(self.button)
        self.button.setEnabled(False)
        #layout.addWidget(self.button)
        
    def create(self):
        self.view.setModel(self.model)
        self.action.setDefaultWidget(self.view)
        self.button.menu().addAction(self.action)





if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.resize(200, 200)
    window.show()
    sys.exit(app.exec_())
