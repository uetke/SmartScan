#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QMainWindow,QApplication,SIGNAL,QTableWidgetItem
from GUI.Logbook.logbookguimainwindow import Ui_MainWindow as logbookGUI

from lib.db_comm import db_comm

class logbookWindow(QMainWindow):
    def __init__(self,session=None,*args):
        QMainWindow.__init__(self, *args)
        self.init = logbookGUI()
        self.init.setupUi(self)
        self.connect(self.init.buttonLogbook,SIGNAL("clicked()"),self.add_entry)
        self.connect(self.init.buttonUser,SIGNAL("clicked()"),self.add_user)
        if session:
            self.db = session['db']
        else:
            self.db = db_comm()
        
        self.users = self.db.get_users()
        self.setups = self.db.get_setups()
        self.entries = self.db.get_entries()
        ent = QTableWidgetItem('String')
        self.init.tableUsers.setRowCount(3)
        self.init.tableUsers.setItem(0,1,ent)
        self.init.tableUsers.setShowGrid(True)
                
        
    def add_entry(self):
        """ Displays a dialog for adding a new entry to the logbook. 
        """
        #TODO: Make dialog and use db_comm
        
    def add_user(self):
        """ Displays a dialog for adding a new user to the database. 
        """ 
        #TODO Make the dialog and use db_comm
        
    def add_setup(self):
        """ Displays a dialog for adding a new setup to the database. 
        """ 
        #TODO: Make the dialaog and use db_comm
        
class App(QtGui.QApplication):
    def __init__(self,session, *args):
        QApplication.__init__(self, *args)
        self.init = logbookWindow(session)
        self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
        self.init.setWindowTitle('Logbook 2.0')
        self.init.show()

    def byebye(self):
        self.exit(0)
        
if __name__ == '__main__':
    app = App(session,sys.argv)
    app.exec_()