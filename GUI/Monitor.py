# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\My Documents\bachelor_project\bitbucket\workspace\Adwin_gui\Monitor.ui'
#
# Created: Tue Apr 22 12:27:40 2014
#	   by: PyQt4 UI code generator 4.9.6
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
	def setupUi(self, MplWidget,MplCanvas,MainWindow):
		MplWidget.setObjectName("MplWidget")
		MplWidget.resize(800, 500)
		self.centralwidget = QtGui.QWidget(MplWidget)
		self.centralwidget.setObjectName("centralwidget")
		self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
		self.verticalLayout.setObjectName("verticalLayout")
		self.frame = QtGui.QFrame(self.centralwidget)
		self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
		self.frame.setFrameShadow(QtGui.QFrame.Raised)
		self.frame.setObjectName("frame")
		self.gridLayout = QtGui.QGridLayout(self.frame)
		self.gridLayout.setObjectName("gridLayout")
		self.verticalLayout.addWidget(self.frame)
		# ------
		self.widget = MplCanvas(MplWidget,MainWindow)
		self.gridLayout.addWidget(self.widget)
		# ------
		#self.widget_2 = NavigationToolbar2QTAgg(self.widget,MplWidget)
		#self.verticalLayout.addWidget(self.widget_2)
		MplWidget.setCentralWidget(self.centralwidget)

		QtCore.QMetaObject.connectSlotsByName(MplWidget)

	def retranslateUi(self, MainWindow):
		MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
		self.actionThis_is_a_monitor.setText(_translate("MainWindow", "This is a monitor", None))
		self.actionQuit_Ctrl_Q.setText(_translate("MainWindow", "Quit Ctrl-Q", None))
		self.actionThis_is_a_monitor_2.setText(_translate("MainWindow", "This is a monitor", None))

