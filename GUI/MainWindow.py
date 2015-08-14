#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QMainWindow,QApplication,SIGNAL,QStandardItem,QFileDialog
from GUI.MplAnimate import MplAnimate

# from Configuration_Window import Ui_MainWindow as Configuration_Window
from GUI.starting_window import Ui_MainWindow as Configuration_Window
from GUI.MainWindowGui import Ui_MainWindow
from lib.xml2dict import device
import numpy as np
from lib.adq_mod import adq
from lib.logger import logger
from lib.db_comm import db_comm

from datetime import datetime

from _private.set_debug import debug

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
        self._session = {} # Dictionary to store session variables
        
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
        self.connect(self.init.search_directory, SIGNAL("clicked()"), self.search_directory)
        self.logger=logger(filelevel=30)
        
        # These variables should be erased. They are being kept for legacy support.
        self.dev_conf = 'config/config_devices.xml'
        self._session['dev_conf'] = 'config/config_devices.xml'
        self.par_conf = 'config/config_variables.xml'
        self._session['par_conf'] = 'config/config_variables.xml'
        # Select the default saving folder
        self.init.save_directory.setText('D:/Data/'+str(datetime.now().date())+'/')
        self.db = db_comm('_private/logbook.db')
        
    def MainWindow(self):
        #self.directory = self.init.save_directory.text()
        self._session['directory'] = self.init.save_directory.text()
        #self.description = self.init.experiment_description.toPlainText()
        self._session['description'] = self.init.experiment_description.toPlainText()
        #self.autoSave = self.init.autoSave.isChecked()
        self._session['autoSave'] = self.init.autoSave.isChecked()
        # Create the directory before starting the program
        if not os.path.exists(self._session['directory']):
            os.makedirs(self._session['directory'])
        
        # Makes the initial logbook entry.
        
        filename = 'logbook.txt'
        f = open(self._session['directory']+filename,'a')
        f.write(self._session['description']+'\n')
        f.close()
        
        self.main = MainWindow(self._session)
        self.main.setWindowTitle('Main')
        self.main.show()
        
    def start(self):
        self.MainWindow()
        self.fileQuit()
        
    def search_directory(self):
        self.save_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.init.save_directory.setText(self.save_dir+'\\'+str(datetime.now().date())+'/')
        
        
    def fileQuit(self):
        self.close()
    
    def about(self):
        QtGui.QMessageBox.about(self, "About","""Scan 2.0 was developed in MoNOS""")

            
class MainWindow(QMainWindow):
    def __init__(self,session,*args):
        self._session = session
        self.dev_conf = session['dev_conf']
        self.par_conf = session['par_conf']
        self.directory = session['directory']
        self.description = session['description']
        self.autoSave = session['autoSave']
        self.evernoteSave = True # TODO
        QMainWindow.__init__(self, *args)
        self.main = Ui_MainWindow()
        self.main.setupUi(self)
                
        self.adw = adq(debug)
        if self.adw.adw.Test_Version() != 1: # Not clear if this means the ADwin is booted or not
            self.adw.boot()
            self.adw.init_port7()
            print('Booting the ADwin...')
            
        
        self.adw.load('lib/adbasic/init_adwin.T98')
        self.adw.start(8)
        self.adw.wait(8)
        self.adw.load('lib/adbasic/monitor.T90')
        self.adw.load('lib/adbasic/adwin.T99')
        self.scanwindows = {}
        self.scanindex = 0
        self.monitor = {}
        
        self.update_devices() # Generates the devices listed in the configuration file
    
    def update_devices(self):
        """ Updates the devices specified in the configuration file. 
        It allows to update devices without restarting the UI. 
        """
        
        self.device_names = device(type='Adwin',filename=self.dev_conf)
        self.devices = {}
        for name in self.device_names.properties:
            self.devices[name] = device(type='Adwin',name=name,filename=self.dev_conf)
        self.init_labels()
    
    def init_labels(self):
        j=0
        k=1
        self.Controler = {}
        self.main.setupUi(self)
        self.update_menu()
#         self.main.Scan_Detector_comboBox.clear()
#         self.main.Controler_Detector_comboBox.clear()
#         self.main.Scan_Dropdown.model.clear()
#         self.main.Scan_1st_comboBox.clear()
#         self.main.Scan_2nd_comboBox.clear()
#         self.main.Scan_3rd_comboBox.clear()
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
    
    def update_menu(self):
        """ Updates the menu of the main screen. It is a workaround the missing menu in the original design file. 
            It should be deprecated in future versions. 
        """
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.file_menu.addAction('&Close all scan windows', self.CloseScans)
        self.menuBar().addMenu(self.file_menu)
        
        self.edit_menu = QtGui.QMenu('&Edit', self)
        self.edit_menu.addAction('&Refresh Devices',self.update_devices, 
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_F5)
        self.edit_menu.addAction('&Edit Defaults',self.edit_defaults,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_E)
        
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.edit_menu)
        
        self.help_menu = QtGui.QMenu('&Help', self)
        self.help_menu.addAction('&About', self.about)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        
    def edit_defaults(self):
        dialog = EditConfig(self)
        dialog.exec_()
        
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
            self.scan = MplAnimate(self,option,['Scan','Line'],self._session,timeindex)
            self.scanwindows[timeindex] = self.scan
        else:
            if self.main.Scan_2nd_comboBox.currentText()=='None':
                self.scan = MplAnimate(self,option,['Scan','Line'],self._session,self.scanindex)
                self.main.Controler_Select_scan.addItem(_translate("MainWindow", 'Window %s'%self.scanindex, None))
                self.scanwindows[self.scanindex] = self.scan
            else:
                self.scan = MplAnimate(self,option,['Scan','Imshow'],self._session,self.scanindex)
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
#         self.main.Controler_Select_scan.clear()
#         for key in self.scanwindows.keys():
#             if not str(key).startswith('T'):
#                 self.main.Controler_Select_scan.addItem(_translate("MainWindow", 'Window %s'%key, None))               
                
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
        self.monitor[option]=MplAnimate(self,option,['Monitor','Line'],self._session)
        self.monitor[option].setWindowTitle(option)
        self.monitor[option].show()
        
    def fileQuit(self):
        reply = QtGui.QMessageBox.question(self, 'Message',"Are you sure you want to quit?", 
                                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass
        
    def closeEvent(self, ce):
        self.fileQuit()
        ce.ignore()
    
class EditConfig(QtGui.QDialog):
    """ Dialog for editing the default values of the application. 
    """
    def __init__(self,inherits,parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.parent = inherits
        
        self.setWindowTitle('Configure scan')
        self.setGeometry(100,100,400,300)
        self.layout = QtGui.QGridLayout(self)
        
        self.title_label = QtGui.QLabel(self)
        self.title_label.setText('Edit the configuration')
        
        self.saveDir_label = QtGui.QLabel(self)
        self.saveDir_label.setText('Save directory')
        self.saveDir = QtGui.QLineEdit(self)
        self.saveDir.setText(self.parent.directory)
        self.saveDir_search = QtGui.QPushButton('...',self)
        
        self.description_label = QtGui.QLabel(self)
        self.description_label.setText('Experiment Description')
        self.description = QtGui.QPlainTextEdit()
        self.description.setPlainText(self.parent.description)
        
        self.autosave_label = QtGui.QLabel(self)
        self.autosave_label.setText('Autosave')
        
        self.autosave = QtGui.QCheckBox(self)
        if self.parent.autoSave:
            self.autosave.setChecked(True) # By default things will be auto-saved
        else:
            self.autosave.setChecked(False)
            
        #self.evernote_save_label = QtGui.QLabel(self)
        #self.evernote_save_label.setText('Save into Evernote')
        
        self.evernote_save = QtGui.QCheckBox(self)
        if self.parent.evernoteSave:
            self.evernote_save.setChecked(True) # By default save into evernote
        else:
            self.evernote_save.setChecked(False)
            
        self.evernote_label = QtGui.QLabel(self)
        self.evernote_label.setText('Evernote username: ')
        self.evernote = QtGui.QLineEdit(self)
        self.evernote.setText("To be implemented...")
#         self.evernote_button = QtGui.QPushButton('Change',self)
#         self.evernote_button.clicked[bool].connect(self.updateEvernote)        
#         
        self.apply_button = QtGui.QPushButton('Apply',self)
        self.apply_button.clicked[bool].connect(self.apply)
        
        self.cancel_button = QtGui.QPushButton('Cancel', self)
        self.cancel_button.clicked[bool].connect(self.cancel)
        self.saveDir_search.clicked.connect(self.search_directory)
        
        self.layout.addWidget(self.title_label,0,0,1,3)
        self.layout.addWidget(self.saveDir_label,1,0,1,1)
        self.layout.addWidget(self.saveDir,1,1,1,1)
        self.layout.addWidget(self.saveDir_search,1,2,1,1)
        self.layout.addWidget(self.description_label,2,0,1,1)
        self.layout.addWidget(self.description,2,1,1,2)
        self.layout.addWidget(self.autosave_label,3,0,1,1)
        self.layout.addWidget(self.autosave,3,1,1,1)
        self.layout.addWidget(self.evernote_label,4,0,1,1)
        self.layout.addWidget(self.evernote,4,1,1,1)
        self.layout.addWidget(self.evernote_save,4,1,1,1)
#         self.layout.addWidget(self.evernote_button,4,2,1,1)
        self.layout.addWidget(self.apply_button,5,0,1,1)
        self.layout.addWidget(self.cancel_button,5,2,1,1)
        self.show()
        
    def apply(self):
        """ Method for updating the edited values. 
        """
        
        self.parent._session['directory'] = self.saveDir.text()
        self.parent._session['description'] = self.description.toPlainText()
        self.parent._session['autoSave'] = self.autosave.isChecked()
        if not os.path.exists(self.parent._session['directory']):
            os.makedirs(self.parent._session['directory'])
        filename = 'logbook.txt'    
       
        f = open(self.parent._session['directory']+filename,'a')
        f.write(self.parent._session['description']+'\n')
        f.close()
        
        self.close()
        
    def cancel(self):
        """ Canceling any changes. 
        """
        self.close()
        
    def search_directory(self):
        save_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.saveDir.setText(save_dir+'\\'+str(datetime.now().date())+'/')
        
    def updateEvernote(self):
        """ Function for updating the evernote login authorization. 
        """
        
class App(QtGui.QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        self.init = InitWindow()
        self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
        self.init.setWindowTitle('Scan 2.0')
        self.init.show()
    
    def byebye(self):
        self.exit(0)

def main(args):
    global app
    app = App(args)
    app.exec_()
    
    
if __name__ == "__main__":
    main(sys.argv)