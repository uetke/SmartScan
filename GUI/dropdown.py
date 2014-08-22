from PyQt4 import QtGui
from PyQt4.Qt import QStandardItemModel, QListView

class dropdown(QtGui.QWidget):
    def __init__(self,pos):
        QtGui.QWidget.__init__(self)
        self.button = QtGui.QToolButton(self)
        self.button.setText('Detectors')
        self.button.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.button.setMenu(QtGui.QMenu(self.button))
        self.model = QStandardItemModel()


        self.view = QListView()
        self.action = QtGui.QWidgetAction(self.button)
        self.button.setEnabled(False)
        
    def create(self):
        self.view.setModel(self.model)
        self.action.setDefaultWidget(self.view)
        self.button.menu().addAction(self.action)
