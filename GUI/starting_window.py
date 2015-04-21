# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\starting_window.ui'
#
# Created: Mon Apr 20 17:24:50 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(344, 323)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.experiment_description = QtGui.QPlainTextEdit(self.centralwidget)
        self.experiment_description.setObjectName(_fromUtf8("experiment_description"))
        self.gridLayout.addWidget(self.experiment_description, 3, 0, 1, 3)
        self.save_directory_label = QtGui.QLabel(self.centralwidget)
        self.save_directory_label.setObjectName(_fromUtf8("save_directory_label"))
        self.gridLayout.addWidget(self.save_directory_label, 0, 0, 1, 1)
        self.save_directory = QtGui.QLineEdit(self.centralwidget)
        self.save_directory.setObjectName(_fromUtf8("save_directory"))
        self.gridLayout.addWidget(self.save_directory, 1, 0, 1, 2)
        self.search_directory = QtGui.QPushButton(self.centralwidget)
        self.search_directory.setObjectName(_fromUtf8("search_directory"))
        self.gridLayout.addWidget(self.search_directory, 1, 2, 1, 1)
        self.experiment_description_label = QtGui.QLabel(self.centralwidget)
        self.experiment_description_label.setObjectName(_fromUtf8("experiment_description_label"))
        self.gridLayout.addWidget(self.experiment_description_label, 2, 0, 1, 1)
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 4, 2, 1, 1)
        self.autoSave = QtGui.QCheckBox(self.centralwidget)
        self.autoSave.setChecked(True)
        self.autoSave.setObjectName(_fromUtf8("autoSave"))
        self.gridLayout.addWidget(self.autoSave, 4, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 344, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.save_directory_label.setBuddy(self.save_directory)
        self.experiment_description_label.setBuddy(self.experiment_description)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.save_directory, self.search_directory)
        MainWindow.setTabOrder(self.search_directory, self.experiment_description)
        MainWindow.setTabOrder(self.experiment_description, self.autoSave)
        MainWindow.setTabOrder(self.autoSave, self.pushButton)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.save_directory_label.setText(_translate("MainWindow", "Directory for saving the files:", None))
        self.search_directory.setText(_translate("MainWindow", "...", None))
        self.experiment_description_label.setText(_translate("MainWindow", "Description of the experiment:", None))
        self.pushButton.setText(_translate("MainWindow", "Continue", None))
        self.autoSave.setText(_translate("MainWindow", "Auto Save", None))

