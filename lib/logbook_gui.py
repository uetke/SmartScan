import sys
from PyQt4 import QtCore, QtGui
from logbook import logbook

class add_user(QtGui.QWidget):
    """ Simple dialog for adding a user to the database of users. 
    """
    def __init__(self,lb,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setWindowTitle('Add a User')
        
        self.layout = QtGui.QGridLayout(self)
        self.name = QtGui.QLineEdit(self)
        self.name_label = QtGui.QLabel(self)
        self.name_label.setText('Add a new user: ')
        
        self.apply_button = QtGui.QPushButton('Apply', self)
        self.cancel_button = QtGui.QPushButton('Cancel', self)
        
        self.layout.addWidget(self.name_label,0,0)
        self.layout.addWidget(self.name,0,1)
        self.layout.addWidget(self.apply_button,1,0)
        self.layout.addWidget(self.cancel_button,1,1)
        
        self.apply_button.clicked[bool].connect(self.AddUser)
        self.cancel_button.clicked[bool].connect(self.close)
        self.lb = lb
        
    def AddUser(self):
        """ Method for adding a user to the logbook. 
        """
        new_user = self.name.text()
        QtGui.QMessageBox.information(self,"Confirm adding","%s added to the users list"%new_user)
        
        self.lb.new_user(new_user)
        
        self.close()
        return
        
class add_setup(QtGui.QWidget):
    """ Simple dialog for adding a new setup to the database. 
    """
    def __init__(self,lb,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setWindowTitle('Add a New Setup')
        
        self.layout = QtGui.QGridLayout(self)
        self.name = QtGui.QLineEdit(self)
        self.name_label = QtGui.QLabel(self)
        self.name_label.setText('Add a new setup: ')
        
        self.description = QtGui.QTextEdit(self)
        
        self.file = QtGui.QLineEdit(self)
        self.file_button = QtGui.QPushButton('...',self)
        
        self.apply_button = QtGui.QPushButton('Apply', self)
        self.cancel_button = QtGui.QPushButton('Cancel', self)
        
        self.layout.addWidget(self.name_label,0,0,1,2)
        self.layout.addWidget(self.name,0,3,1,2)
        self.layout.addWidget(self.description,1,0,1,5)
        self.layout.addWidget(self.file,2,0,1,4)
        self.layout.addWidget(self.file_button,2,4)
        self.layout.addWidget(self.apply_button,3,0,1,3)
        self.layout.addWidget(self.cancel_button,3,3,1,3)
        
        self.apply_button.clicked[bool].connect(self.AddUser)
        self.cancel_button.clicked[bool].connect(self.close)
        self.file_button.clicked.connect(self.SelectFile)
        self.lb = lb
        
    def SelectFile(self):
        """ Updates the selected file. 
        """
        
        self.file.setText(QtGui.QFileDialog.getOpenFileName())
        
    def AddUser(self):
        """ Method for adding a new setup to the logbook. 
        """
        new_setup = self.name.text()
        new_description = self.description.toPlainText()
        new_file = self.file.text()
        QtGui.QMessageBox.information(self,"Confirm adding","Added %s to the setup list"%new_setup)
        self.lb.new_setup(new_setup,new_description,file=new_file)
        self.close()
        return
        
if __name__ == '__main__': 
    lb = logbook('P:')
    app = QtGui.QApplication(sys.argv)
    #ad = add_user(lb)
    #ad.show()
    se = add_setup(lb)
    se.show()
    app.exec_()