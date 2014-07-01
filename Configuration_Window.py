# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\My Documents\bachelor_project\bitbucket\workspace\Adwin basics\Configuration_Window.ui'
#
# Created: Thu May  8 10:59:13 2014
#      by: PyQt4 UI code generator 4.9.6
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
        MainWindow.resize(427, 273)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 401, 223))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.Par_conf_label = QtGui.QLabel(self.gridLayoutWidget)
        self.Par_conf_label.setObjectName(_fromUtf8("Par_conf_label"))
        self.gridLayout.addWidget(self.Par_conf_label, 3, 0, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setStyleSheet(_fromUtf8("font: 12pt \"MS Shell Dlg 2\";"))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 2)
        self.Dev_conf_label = QtGui.QLabel(self.gridLayoutWidget)
        self.Dev_conf_label.setObjectName(_fromUtf8("Dev_conf_label"))
        self.gridLayout.addWidget(self.Dev_conf_label, 2, 0, 1, 1)
        self.Dev_conf_Edit = QtGui.QPlainTextEdit(self.gridLayoutWidget)
        self.Dev_conf_Edit.setObjectName(_fromUtf8("Dev_conf_Edit"))
        self.gridLayout.addWidget(self.Dev_conf_Edit, 2, 1, 1, 1)
        self.pushButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButton.setAutoDefault(True)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 4, 0, 1, 2)
        self.Par_conf_Edit = QtGui.QPlainTextEdit(self.gridLayoutWidget)
        self.Par_conf_Edit.setObjectName(_fromUtf8("Par_conf_Edit"))
        self.gridLayout.addWidget(self.Par_conf_Edit, 3, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 427, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.pushButton, self.Dev_conf_Edit)
        MainWindow.setTabOrder(self.Dev_conf_Edit, self.Par_conf_Edit)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.Par_conf_label.setText(_translate("MainWindow", "Parameter names configuration file", None))
        self.label.setText(_translate("MainWindow", "Configuration files", None))
        self.Dev_conf_label.setText(_translate("MainWindow", "Device configuration file", None))
        self.Dev_conf_Edit.setPlainText(_translate("MainWindow", "config_devices.xml", None))
        self.pushButton.setText(_translate("MainWindow", "Start", None))
        self.Par_conf_Edit.setPlainText(_translate("MainWindow", "config_variables.xml", None))

