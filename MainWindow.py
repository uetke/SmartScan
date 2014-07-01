#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QMainWindow,QApplication,SIGNAL,QStandardItem
from MplAnimate import MplAnimate
from Configuration_Window import Ui_MainWindow as Configuration_Window
from MainWindowGui import Ui_MainWindow
from xml2dict import device,variables
import numpy as np
from adq_functions import adq,inter_add_remove
from logger import get_all_caller,logger
import codecs


def _fromUtf8(s):
	return s

try:
	_encoding = QtGui.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig)
		
class InitWindow(QMainWindow):
	def __init__(self,*args):
		QMainWindow.__init__(self, *args)
		self.init = Configuration_Window()
		self.init.setupUi(self)
		self.file_menu = QtGui.QMenu('&File', self)
		self.file_menu.addAction('&Quit', self.fileQuit,
								 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
		self.menuBar().addMenu(self.file_menu)

		self.help_menu = QtGui.QMenu('&Help', self)
		self.menuBar().addSeparator()
		self.menuBar().addMenu(self.help_menu)

		self.help_menu.addAction('&About', self.about)
		self.connect(self.init.pushButton, SIGNAL("clicked()"), self.start)
		self.logger=logger(filelevel=20)
		
	def MainWindow(self):
		self.dev_conf = self.init.Dev_conf_Edit.toPlainText()
		self.par_conf = self.init.Par_conf_Edit.toPlainText()
		self.main = MainWindow(self.dev_conf,self.par_conf)
		self.main.setWindowTitle('Main')
		self.main.show()
		
	def start(self):
		self.MainWindow()
		self.fileQuit()
		
	def fileQuit(self):
		self.close()
	
	def about(self):
		QtGui.QMessageBox.about(self, "About","""In this window the user has to give the configuration files""")

			
class MainWindow(QMainWindow):
	def __init__(self,dev_conf,par_conf, *args):
		self.dev_conf = dev_conf
		self.par_conf = par_conf
		QMainWindow.__init__(self, *args)
		self.main = Ui_MainWindow()
		self.main.setupUi(self)
		self.file_menu = QtGui.QMenu('&File', self)
		self.file_menu.addAction('&Quit', self.fileQuit,
								 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
		self.file_menu.addAction('&Close all scan windows', self.CloseScans)
		self.menuBar().addMenu(self.file_menu)

		self.help_menu = QtGui.QMenu('&Help', self)
		self.menuBar().addSeparator()
		self.menuBar().addMenu(self.help_menu)
		self.device_names = device(type='Adwin',filename=self.dev_conf)
		self.devices = {}
		for name in self.device_names.properties:
			self.devices[name] = device(type='Adwin',name=name,filename=self.dev_conf)
		self.adw = adq('adwin.T99') 
		self.adw.load()
		self.scanwindows = {}
		self.scanindex = 0
		self.monitor = {}
		self.init_labels()

	def init_labels(self):
		j=0
		k=1
		self.Controler = {}
		for i in sorted(self.devices):
			i = self.devices[i].properties
			if 'Input' in i.keys():
				self.main.Scan_Detector_comboBox.addItem(_fromUtf8(""))
				self.main.Scan_Detector_comboBox.setItemText(j, _translate("MainWindow", i['Name'], None))
				self.main.Monitor_comboBox.addItem(_fromUtf8(""))
				self.main.Monitor_comboBox.setItemText(j, _translate("MainWindow", i['Name'], None))
				self.main.Controler_Detector_comboBox.addItem(_fromUtf8(""))
				self.main.Controler_Detector_comboBox.setItemText(j, _translate("MainWindow", i['Name'], None))
				item = QStandardItem(i['Name'])
				item.setCheckable(True)
				item.setEditable(False)
				self.main.Scan_Dropdown.model.appendRow(item)
				if j==0:
					self.main.Scan_Detector_UnitLabel.setText(_translate("MainWindow", i['Input']['Calibration']['Unit'], None))
				j +=1
			if 'Output' in i.keys():
				unit = i['Output']['Calibration']['Unit']
				self.main.Scan_1st_comboBox.addItem(_translate("MainWindow", i['Name'], None))
				self.main.Scan_2nd_comboBox.addItem(_translate("MainWindow", i['Name'], None))
				self.main.Scan_3rd_comboBox.addItem(_translate("MainWindow", i['Name'], None))
				self.main.Controler_1st_comboBox.addItem(_translate("MainWindow", i['Name'], None))
				self.main.Controler_2nd_comboBox.addItem(_translate("MainWindow", i['Name'], None))
				self.main.Controler_3rd_comboBox.addItem(_translate("MainWindow", i['Name'], None))
				self.Controler[i['Name']] = {'NameLabel': None,'PosBox': None,'IncBox': None
											,'UnitLabel': None,'AddButton': None,'MinButton': None}
				self.Controler[i['Name']]['NameLabel'] = QtGui.QLabel(self.main.gridLayoutWidget_2)
				self.Controler[i['Name']]['NameLabel'].setObjectName(_fromUtf8("Controler_NameLabeln_%s" %i['Name']))
				self.main.Controler_gridLayout.addWidget(self.Controler[i['Name']]['NameLabel'], k+5, 0, 1, 1)
				self.Controler[i['Name']]['NameLabel'].setText(_translate("MainWindow", i['Name'], None))
				
				self.Controler[i['Name']]['PosBox'] = QtGui.QDoubleSpinBox(self.main.gridLayoutWidget_2)
				self.Controler[i['Name']]['PosBox'].setObjectName(_fromUtf8("Controler_Pos_doubleSpinBoxn_%s" %i['Name']))
				self.Controler[i['Name']]['PosBox'].setKeyboardTracking(False)
				self.Controler[i['Name']]['PosBox'].setSuffix(" " + unit)
				self.main.Controler_gridLayout.addWidget(self.Controler[i['Name']]['PosBox'], k+5, 1, 1, 1)
				
				self.Controler[i['Name']]['IncBox'] = QtGui.QDoubleSpinBox(self.main.gridLayoutWidget_2)
				self.Controler[i['Name']]['IncBox'].setObjectName(_fromUtf8("Controler_Inc_doubleSpinBoxn_%s" %i['Name']))
				self.Controler[i['Name']]['IncBox'].setSingleStep(0.05)
				self.Controler[i['Name']]['IncBox'].setSuffix(" " + unit)
				self.main.Controler_gridLayout.addWidget(self.Controler[i['Name']]['IncBox'], k+5, 2, 1, 1)

				self.Controler[i['Name']]['AddButton'] = QtGui.QPushButton(self.main.gridLayoutWidget_2)
				self.Controler[i['Name']]['AddButton'].setEnabled(True)
				self.Controler[i['Name']]['AddButton'].setObjectName(_fromUtf8("Controler_Add_pushButton_%s" %i['Name']))
				self.main.Controler_gridLayout.addWidget(self.Controler[i['Name']]['AddButton'], k+5, 3, 1, 1)
				self.Controler[i['Name']]['AddButton'].setText(_translate("MainWindow", "+", None))
				
				self.Controler[i['Name']]['MinButton'] = QtGui.QPushButton(self.main.gridLayoutWidget_2)
				self.Controler[i['Name']]['MinButton'].setEnabled(True)
				self.Controler[i['Name']]['MinButton'].setObjectName(_fromUtf8("Controler_Min_pushButtonn_%s" %i['Name']))
				self.main.Controler_gridLayout.addWidget(self.Controler[i['Name']]['MinButton'], k+5, 4, 1, 1)
				self.Controler[i['Name']]['MinButton'].setText(_translate("MainWindow", "-", None))

				QtCore.QObject.connect(self.Controler[i['Name']]['AddButton'], QtCore.SIGNAL("clicked()"), self.ChangePos)	 
				QtCore.QObject.connect(self.Controler[i['Name']]['MinButton'], QtCore.SIGNAL("clicked()"), self.ChangePos)
				QtCore.QObject.connect(self.Controler[i['Name']]['PosBox'],QtCore.SIGNAL("valueChanged(double)"),self.ChangePos) 
				k +=1
		
				
		self.help_menu.addAction('&About', self.about)
		self.connect(self.main.Monitor_pushButton, SIGNAL("clicked()"), self.Monitor)
		QtCore.QObject.connect(self.main.Scan_Detector_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.ChangeUnit)
		QtCore.QObject.connect(self.main.Scan_1st_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.ChangeUnit)					
		QtCore.QObject.connect(self.main.Scan_2nd_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.ChangeUnit)					
		QtCore.QObject.connect(self.main.Scan_3rd_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.ChangeUnit)
		QtCore.QObject.connect(self.main.Scan_start_pushButton, QtCore.SIGNAL("clicked()"), self.StartScan)	  
		QtCore.QObject.connect(self.main.Scan_stop_pushButton, QtCore.SIGNAL("clicked()"), self.StopScan)
		QtCore.QObject.connect(self.main.Scan_Mult_Detector_comboBox, QtCore.SIGNAL("clicked()"), self.Mult_detect)		
		QtCore.QObject.connect(self.main.Controler_Go, QtCore.SIGNAL("clicked()"), self.Go2Pos)
		QtCore.QObject.connect(self.main.Controler_Refocus, QtCore.SIGNAL("clicked()"), self.Refocus)	
		
		self.main.Scan_Dropdown.create()
		self.InitDevices()
		
	def InitDevices(self):
		for i in sorted(self.devices):
			device = self.devices[i].properties
			if 'Output' in device.keys():
				name = device['Name']
				self.Controler[name]['PosBox'].setValue(device['Output']['Calibration']['Init'])
			
	def Mult_detect(self):
		if self.main.Scan_Mult_Detector_comboBox.isChecked():
			self.main.Scan_Detector_comboBox.setEnabled(False)
			self.main.Scan_Dropdown.button.setEnabled(True)
			self.main.Scan_Detector_UnitLabel.setEnabled(False)
		else:
			self.main.Scan_Detector_comboBox.setEnabled(True)
			self.main.Scan_Dropdown.button.setEnabled(False)
			self.main.Scan_Detector_UnitLabel.setEnabled(True)
			
			
	def StartScan(self):
		self.main.Controler_BusyLabel.setText(_translate("MainWindow", "Busy", None))
		self.main.Scan_start_pushButton.setEnabled(False)
		self.main.Controler_Refocus.setEnabled(False)
		self.main.Controler_Go.setEnabled(False)
		for name in self.Controler.keys():
			self.Controler[name]['AddButton'].setEnabled(False)
			self.Controler[name]['MinButton'].setEnabled(False)
			self.Controler[name]['PosBox'].setEnabled(False)
		
		option = '%s;%s' %(self.main.Scan_Detector_comboBox.currentText(),self.main.Scan_1st_comboBox.currentText())
		if not self.main.Scan_2nd_comboBox.currentText()=='None':
			option += ' and on the y-axes the %s.' %self.main.Scan_2nd_comboBox.currentText()
		if self.main.Scan_1st_comboBox.currentText()=='Time':
			timeindex = 'Timetrace%s' %self.scanindex
			self.scan = MplAnimate(self,option,['Scan','Line'],timeindex)
			self.scanwindows[timeindex] = self.scan
		else:
			self.scan = MplAnimate(self,option,['Scan','Imshow'],self.scanindex)
			self.main.Controler_Select_scan.addItem(_translate("MainWindow", 'Window %s'%self.scanindex, None))
			self.scanwindows[self.scanindex] = self.scan
		self.scan.setWindowTitle("Window %s: Scan with the %s Detector with on the x-axes %s" %(tuple([self.scanindex])+tuple(option.split(';'))))
		self.scanindex += 1 
		self.scan.show()
		
	def StopScan(self):
		self.main.Controler_BusyLabel.setText(_translate("MainWindow", "", None))
		self.main.Scan_start_pushButton.setEnabled(True)
		self.main.Controler_Refocus.setEnabled(True)
		self.main.Controler_Go.setEnabled(True)
		for name in self.Controler.keys():
			self.Controler[name]['AddButton'].setEnabled(True)
			self.Controler[name]['MinButton'].setEnabled(True)
			self.Controler[name]['PosBox'].setEnabled(True)
		self.scan.animation.stop()
		self.adw.stop(9)
		self.main.Controler_Select_scan.clear()
		for key in self.scanwindows.keys():
			if not str(key).startswith('T'):
				self.main.Controler_Select_scan.addItem(_translate("MainWindow", 'Window %s'%key, None))
			
				
	def CloseScans(self):
		values = list(self.scanwindows.values())
		for i in values:
			if i.isRunning():
				i.fileQuit()
		self.scanwindows = {}
		self.scanindex = 0
			
	def Go2Pos(self):
		index = int(self.main.Controler_Select_scan.currentText().split()[-1])
		linePos = self.scanwindows[index].widget.linePos
		for key,value in linePos.items():
			self.Controler[key]['PosBox'].setValue(value)
		
	def Refocus(self):
		index = int(self.main.Controler_Select_scan.currentText().split()[-1])
		linePos = self.scanwindows[index].widget.linePos
		detector = device(self.main.Controler_Detector_comboBox.currentText())
		dir1 = self.main.Controler_1st_comboBox.currentText()
		dir2 = self.main.Controler_2nd_comboBox.currentText()
		dir3 = self.main.Controler_3rd_comboBox.currentText()
		ref = {}
		ref[dir1] = linePos.get(dir1,self.Controler[dir1]['PosBox'].value())
		if not dir2=='None':
			ref[dir2] = linePos.get(dir2,self.Controler[dir2]['PosBox'].value())
		if not dir2=='None':
			ref[dir3] = linePos.get(dir3,self.Controler[dir3]['PosBox'].value())
		devs = np.array([])
		center = np.array([])
		for key,value in ref.items():
			devs = np.append(devs,device(key))
			center = np.append(center,value)
		new_center = self.adw.focus_full(detector,devs,center,1*np.ones(len(devs)),.05*np.ones(len(devs)))
		for idx,dev in enumerate(devs):
			self.Controler[dev.properties['Name']]['PosBox'].setValue(new_center[idx])
			
		
		
	def ChangePos(self):
		names = self.sender().objectName().split('_')
		if names[1]=='Add':
			self.Controler[names[3]]['PosBox'].setValue(self.Controler[names[3]]['PosBox'].value() + self.Controler[names[3]]['IncBox'].value())
		elif names[1]=='Min':
			self.Controler[names[3]]['PosBox'].setValue(self.Controler[names[3]]['PosBox'].value() - self.Controler[names[3]]['IncBox'].value())
		else:
			self.adw.set_device_value(self.devices[names[3]], self.Controler[names[3]]['PosBox'].value())
			
	def ChangeUnit(self):
		for i in sorted(self.devices):
			i = self.devices[i].properties
			if self.sender().currentText()==i['Name']:
				if 'Input' in i.keys(): 
					unit = i['Input']['Calibration']['Unit']
				elif 'Output' in i.keys(): 
					unit = i['Output']['Calibration']['Unit']
			elif self.sender().currentText()=='Time':
				unit = 's'
			elif self.sender().currentText()=='None':
				unit = 'None'
		if self.sender().objectName()=='Scan_Detector_comboBox':
			self.main.Scan_Detector_UnitLabel.setText(_translate("MainWindow", unit, None))
		elif self.sender().objectName()=='Scan_1st_comboBox':
			if self.sender().currentText()=='Time':
				self.main.Scan_1st_Accuracy.setEnabled(False)
			else:
				self.main.Scan_1st_Accuracy.setEnabled(True)
			self.main.Scan_1st_UnitLabel.setText(_translate("MainWindow", unit, None))
		elif self.sender().objectName()=='Scan_2nd_comboBox':
			self.main.Scan_2nd_UnitLabel.setText(_translate("MainWindow", unit, None))
		elif self.sender().objectName()=='Scan_3rd_comboBox':
			self.main.Scan_3rd_UnitLabel.setText(_translate("MainWindow", unit, None))
			
	def about(self):
		QtGui.QMessageBox.about(self, "About","""Main window where the user can make a scan, see a signal trough the monitor and finally the user can control the devices.""")


	def Monitor(self):
		option = self.main.Monitor_comboBox.currentText()
		if option in self.monitor.keys():
			if self.monitor[option].isRunning():
				self.monitor[option].fileQuit()
		self.monitor[option]=MplAnimate(self,option,['Monitor','Line'])
		self.monitor[option].setWindowTitle(option)
		self.monitor[option].show()
		
	def fileQuit(self):
		reply = QtGui.QMessageBox.question(self, 'Message',"Are you sure to quit?", 
										QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			sys.exit()
		else:
			pass
		
	def closeEvent(self, ce):
		self.fileQuit()
		ce.ignore()
	
class App(QtGui.QApplication):
	def __init__(self, *args):
		QApplication.__init__(self, *args)
		self.init = InitWindow()
		self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
		self.init.setWindowTitle('Main')
		self.init.show()
	
	def byebye(self):
		self.exit(0)

def main(args):
	global app
	app = App(args)
	app.exec_()
	
	
if __name__ == "__main__":
	main(sys.argv)