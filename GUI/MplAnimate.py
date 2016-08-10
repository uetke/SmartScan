# Python Qt4 bindings for GUI objects
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import QGridLayout

import matplotlib
import matplotlib.pyplot as plt
import os
import math as m
from datetime import datetime

#from matplotlib.figure import Figure
#import matplotlib.animation as animation
import pyqtgraph as pg

import numpy as np

from lib.adq_mod import adq
from lib.xml2dict import device
from lib.config import VARIABLES


# specify the use of PyQt
matplotlib.rcParams['backend.qt4'] = "PyQt4"
#import time
import copy
import codecs

from _private.set_debug import debug

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class MplAnimate(QtGui.QMainWindow):
    def __init__(self, MainWindow, name, option, session, scanindex=-1, parent=None):
        super(MplAnimate, self).__init__(parent)
        #self.ui = Ui_MainWindow()
        #QtGui.QGraphicsObject.__init__(self)
        self.MainWindow = MainWindow
        self.name = name
        self.option = option
        self.scanindex = scanindex
        self._session = session
        self.widget = MplCanvas(self,self._session,MainWindow)
        self.resize(700,450)
        self.setWindowTitle('pyqtgraph example: ImageView')
        #self.ui.setupUi(self,MplCanvas,MainWindow)
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.file_menu.addAction('&Save', self.saveDialog,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self._running = True
        self.key = None

        window_type = self.widget.get_window_type()

        if window_type == 'monitor':
            self.animation = self.widget.monitor()
            self.help_menu.addAction('&About', self.about_monitor)
        elif window_type == 'timetrace':
            self.animation = self.widget.animate_plot()
            self.help_menu.addAction('&About', self.about_scan)
        elif window_type == '1d scan':
            self.animation = self.widget.animate_1dscan()
            self.help_menu.addAction('&About', self.about_scan)
        else:
            self.animation = self.widget.animate_scan()
            self.help_menu.addAction('&About', self.about_scan)

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            self.key = event.key()
            event.accept()
        else:
            self.key = None
            event.ignore()

    def keyReleaseEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            self.key = None
            event.accept()
        else:
            self.key = None
            event.ignore()

    def isRunning(self):
        return self.widget._running

    def saveDialog(self,autosave=False):
        """ This function will run whenever a scan stops and the autoSave option is established.
            It relies in the _session variable to get the directory where to save data.
            Data will be saved as YYMMDDhhmm#.dat
            If the dialog is open by a mouse click, then the dialog for choosing the folder and filename will appear.
        """

        directory = self._session['directory']
        now = datetime.now()
        i = 1
        name = now.strftime('%y%m%d%H%M')
        detectors = self.widget.detector[0].properties['Name']
        variables = ''
        filename = name
        while os.path.exists(os.path.join(directory,filename+".dat")):
            filename = '%s_%s' %(name,i)
            i += 1
        filename += '.dat'
        if not autosave:
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', directory)
        else:
            filename = os.path.join(directory,filename)

        if self.option[1]=='Imshow':
            data = self.widget.data[0]
            header = '#The detector is %s\n#Format 2d array of image\n#x-axis %s (%s ), y-axis %s (%s )\n#center %s, dims %s, accuracy %s, delay %s\n' %(self.widget.detector[0].properties['Name'],self.widget.xlabel,self.widget.xunit,self.widget.ylabel,self.widget.yunit,self.widget.center,self.widget.dims,self.widget.accuracy,self.widget.delay)
            variables = '%s, %s'%(self.widget.xlabel,self.widget.ylabel)
        elif self.option[1]=='Line':
            data = np.vstack((self.widget.xdata[0],self.widget.ydata[0])).T
            header = '#The detector is %s\n#Format x-axis,yaxis\n#x-axis %s (%s ), y-axis %s (%s )' %(self.widget.detector[0].properties['Name'],self.widget.xlabel,self.widget.xunit,list(self.widget.ylabel)[0],list(self.widget.yunit)[0])
            if not self.option[0]=='Monitor' and self.widget.direction_1=='Time':
                header += '#duration %s, accuracy %s\n' %(self.widget.duration,self.widget.accuracy)
            variables = '%s'%(self.widget.xlabel)
        for i in range(1,len(self.widget.detector)):
            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
            header += '#The %s detector is %s\n' %(ordinal(i+1),self.widget.detector[i].properties['Name'])
            detectors += ', %s' % (self.widget.detector[i].properties['Name'])
            if self.option[1]=='Imshow':
                data = np.vstack((data,self.widget.data[i]))
            elif self.option[1]=='Line':
                header += '#x-axis %s (%s ), y-axis %s (%s )\n' %(self.widget.xlabel,self.widget.xunit,list(self.widget.ylabel)[i],list(self.widget.yunit)[i])
                temp = np.vstack((self.widget.xdata[i],self.widget.ydata[i])).T
                data = np.vstack((data,temp))
        if len(self.widget.detector) > 1:
            header += '#Note this file contains multiple (%s) plots\n#Number of lines for a plot is %s\n' %(len(self.widget.detector),data.shape[0]/len(self.widget.detector))

        file_output = codecs.open(filename, 'w', 'utf-8')
        file_output.write(header)
        file_output.close()
        file_output = open(filename,'a+b')
        np.savetxt(file_output, data, '%s', ',')

        entry = {}
        entry['user'] = self._session['userId']
        entry['setup'] = self._session['setupId']
        entry['entry'] = 'Saved scan'
        entry['file'] = filename
        entry['detectors'] = detectors
        entry['variables'] = variables
        if autosave:
            entry['comments'] = 'Autosave'
        else:
            entry['comments'] = 'Manually saved'

        self._session['db'].new_entry(entry)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        if self.isRunning:
            self.animation.stop()
            if self.option[0]=='Scan':
                del self.MainWindow.scanwindows[self.scanindex]
                self.MainWindow.StopScan()
        else:
            if self.option[0]=='Scan':
                del self.MainWindow.scanwindows[self.scanindex]

        self.MainWindow.main.Controler_Select_scan.clear()
        for key in self.MainWindow.scanwindows.keys():
            if not str(key).startswith('T'):
                self.MainWindow.main.Controler_Select_scan.addItem(_translate("MainWindow", 'Window %s'%key, None))

    def about_scan(self):
        print(tuple(self.name.split('-')))
        QtGui.QMessageBox.about(self, "About","""Scan with the %s Detector with on the x-axes %s""" %tuple(self.name.split(';')))

    def about_monitor(self):
        QtGui.QMessageBox.about(self, "About","""Monitor of the %s""" %self.name)

class MplCanvas(QtGui.QGraphicsObject):
    def __init__(self, MplAnimate,session,parent=None):
        #super(MplCanvas, self).__init__(self.imv)
        QtGui.QGraphicsObject.__init__(self)
        self.setParent(parent)
        self.parent = parent
        self.xdata = []
        self.ydata = []
        self.MplAnimate = MplAnimate
        self._running = True
        self.autosave = session['autoSave']
        self.adw=session['adw']
        self.adw.adw.Fifo_Clear(VARIABLES['fifo']['Scan_data'])
        self.par = VARIABLES['par']
        self.continuous = False # Variable to know if starting continuous scans
        
        if MplAnimate.option[0]=='Monitor':
            #TODO: Verify the time delay for low priority processes.
            self.delay = 10E-3 #in s
            self.monitor_process_delay = m.floor(self.delay/self.adw.time_low)
            self.adw.adw.Set_Processdelay(10,self.monitor_process_delay)
            
            #self.delay=400*self.adw.time_low
            self.detector = [device(parent.main.Monitor_comboBox.currentText())]
            self.fifo_name = '%s%i' %(self.detector[0].properties['Type'],self.detector[0].properties['Input']['Hardware']['PortID'])
            self.xlabel = "Time"
            self.xunit = ' s'
            self.ylabel = "%s" %parent.main.Monitor_comboBox.currentText()
            self.yunit = ' %s' %self.detector[0].properties['Input']['Calibration']['Unit']
            self.adw.start(10)

        else:
            #self.adw.load('lib/adbasic/adwin.T99')
            if not self.parent.main.Scan_Dropdown.button.isEnabled():
                self.detector = [device(self.parent.main.Scan_Detector_comboBox.currentText())]
            else:
                i = 0
                self.parent.main.Scan_Dropdown.model
                self.detector = []
                while self.parent.main.Scan_Dropdown.model.item(i):
                    if self.parent.main.Scan_Dropdown.model.item(i).checkState():
                        self.detector.append(device(self.parent.main.Scan_Dropdown.model.item(i).text()))
                    i += 1
            self.direction_1 = self.parent.main.Scan_1st_comboBox.currentText()

            if self.parent.main.Scan_1st_comboBox.currentText()=='Time':
                self.duration = self.parent.main.Scan_1st_Range.value()
                self.accuracy = self.parent.main.Scan_Delay_Range.value()/1000
                self.delay = self.accuracy
                self.xlabel = "%s" %self.parent.main.Scan_1st_comboBox.currentText()
                self.xunit = ' %s' %self.parent.main.Scan_1st_UnitLabel.text()
                self.ylabel = ["%s" %self.detector[i].properties['Name'] for i in range(len(self.detector))]
                self.yunit = [' %s' %self.detector[i].properties['Input']['Calibration']['Unit'] for i in range(len(self.detector))]

            else:
                self.devs = [device(self.parent.main.Scan_1st_comboBox.currentText())]
                self.center = [self.parent.Controler[self.parent.main.Scan_1st_comboBox.currentText()]['PosBox'].value()]
                self.dims = [self.parent.main.Scan_1st_Range.value()]
                self.accuracy = [self.parent.main.Scan_1st_Accuracy.value()]
                self.xlabel = "%s" %parent.main.Scan_1st_comboBox.currentText()
                self.xunit = ' %s' %self.devs[0].properties['Output']['Calibration']['Unit']
                self.ylabel = ["%s" %self.detector[i].properties['Name'] for i in range(len(self.detector))]
                self.yunit = [' %s' %self.detector[i].properties['Input']['Calibration']['Unit'] for i in range(len(self.detector))]
                if not self.parent.main.Scan_2nd_comboBox.currentText()=='None':
                    self.devs.append(device(self.parent.main.Scan_2nd_comboBox.currentText()))
                    self.center.append(self.parent.Controler[self.parent.main.Scan_2nd_comboBox.currentText()]['PosBox'].value())
                    self.dims.append(self.parent.main.Scan_2nd_Range.value())
                    self.accuracy.append(self.parent.main.Scan_2nd_Accuracy.value())
                    self.ylabel = "%s" %parent.main.Scan_2nd_comboBox.currentText()
                    self.yunit = ' %s' %self.devs[1].properties['Output']['Calibration']['Unit']

                if not self.parent.main.Scan_3rd_comboBox.currentText()=='None' and not self.parent.main.Scan_3rd_comboBox.currentText()=='Time':
                    self.devs.append(device(self.parent.main.Scan_3rd_comboBox.currentText()))
                    self.center.append(self.parent.Controler[self.parent.main.Scan_3rd_comboBox.currentText()]['PosBox'].value())
                    self.dims.append(self.parent.main.Scan_3rd_Range.value())
                    self.accuracy.append(self.parent.main.Scan_3rd_Accuracy.value())
                elif self.parent.main.Scan_3rd_comboBox.currentText()=='Time':
                    self.continuous = True
                self.speed = self.parent.main.Scan_Delay_Range.value()
                self.delay = self.speed
            self.fifo_name='scan_data'


    def get_window_type(self):
        if self.MplAnimate.option[0]=='Monitor':
            window_type = 'monitor'
        if self.MplAnimate.option[0]=='Scan' and self.parent.main.Scan_1st_comboBox.currentText()=='Time':
            window_type = 'timetrace'
        elif self.MplAnimate.option[0]=='Scan' and self.parent.main.Scan_2nd_comboBox.currentText()=='None':
            window_type = '1d scan'
        elif self.MplAnimate.option[0]=='Scan':
            window_type = '2d+ scan'

        return window_type

    def get_data(self):
        final_data = []
        window_type = self.get_window_type()
        if window_type == 'monitor':
            data = [self.adw.get_fifo(VARIABLES['fifo'][self.fifo_name])]
        if window_type == 'timetrace':
            data = self.adw.get_timetrace_dynamic(self.detector,self.duration,self.accuracy)
        elif window_type == '1d scan':
            data = copy.copy(self.adw.scan_dynamic(self.detector,self.devs,self.center,self.dims,self.accuracy,self.speed))
        elif window_type == '2d+ scan':
            data = copy.copy(self.adw.scan_dynamic(self.detector,self.devs,self.center,self.dims,self.accuracy,self.speed))
                
        if type(data)==type(False) and data==0:
            self.MplAnimate.close()
            return False
        
        for i in range(len(self.detector)):
            calibration = self.detector[i].properties['Input']['Calibration']
            data[i] = (data[i]-calibration['Offset'])/calibration['Slope']
            if self.detector[i].properties['Type']=='Counter':
                data[i] /= self.delay
            if window_type == 'monitor':
                xdata = np.arange(len(data[i]))*self.delay
                final_data = np.vstack((xdata,data[i]))
            elif window_type == 'timetrace':
                xdata = np.arange(len(data[i]))*self.delay
                final_data.append(np.vstack((xdata,data[i])))
            elif window_type == '1d scan':
                xdata = np.arange(0, self.dims[0], self.accuracy[0]) + self.center[0]
                final_data.append(np.vstack((xdata,data[i])))
            else:
                final_data.append(data[i])

        if not bool(self.adw.adw.Process_Status(9)) and self.MplAnimate.option[0]=='Scan':
            self.adw.running = False
            self.timer.stop()
            self._running = False
            if self.continuous:
                self.MplAnimate.MainWindow.continuousScan()
                #self.emit( QtCore.SIGNAL('ContinuousFinish'))
            else:
                self.MplAnimate.MainWindow.StopScan()
                if self.autosave:
                    def do_autosave():
                        self.MplAnimate.saveDialog(True)

                    # autosave in a moment, when the calling function has updated the
                    QtCore.QTimer.singleShot(200, do_autosave)
            
        return final_data


    def monitor_plot(self):
        temp = self.get_data()
        #temp = [np.arange(500),np.random.rand(500)]
        try:
            self.xdata = np.append(self.xdata,temp[0]+max(self.xdata)+self.delay)
        except:
            self.xdata = np.array([])
            self.ydata = np.array([])
            self.xdata = np.append(self.xdata,temp[0]+self.delay)
        self.ydata = np.append(self.ydata,temp[1])
        if self.MplAnimate.option[0]=='Monitor':
            self.xdata = self.xdata[-500:]
            self.ydata = self.ydata[-500:]
        self.lineplot.setData(y=self.ydata,x=self.xdata)
        self.plotwidget.plotItem.removeItem(self.text)
        self.text = pg.TextItem(html='<div style="text-align: center"><span style="color: #FFF; font-size: 40pt;">%.2E </span></div>' %self.ydata[-1], anchor=(-0.3,1.3), border='w', fill=(0, 0, 255, 100))
        diff_x = np.max(self.xdata) - np.min(self.xdata)
        diff_y = np.max(self.ydata) - np.min(self.ydata)
        self.text.setPos(self.xdata.min()-0.1*diff_x,self.ydata.max()-0.2*diff_y)
        self.plotwidget.plotItem.addItem(self.text)

    def func_plot(self):
        temp = self.get_data()
        #temp = [np.arange(500),np.random.rand(500)]
        for i in range(len(self.detector)):
            try:
                self.xdata[i] = np.append(self.xdata[i],temp[i][0]+max(self.xdata[i])+self.delay)
            except:
                self.xdata.append(np.array([]))
                self.ydata.append(np.array([]))
                self.xdata[i] = np.append(self.xdata[i],temp[i][0]+self.delay)
            self.ydata[i] = np.append(self.ydata[i],temp[i][1])
            self.lineplot[i].setData(y=self.ydata[i],x=self.xdata[i])

    def scan_plot1d(self):
        data = np.array(self.get_data())
        self.xdata = data[:,0]
        self.ydata = data[:,1]
        for i in range(len(self.detector)):
            self.lineplot[i].setData(y=self.ydata[i],x=self.xdata[i])


    def init_scan(self):
        temp = self.get_data()
        #temp = np.random.normal(size=(200, 200))
        self.pos = np.array(self.center)-0.5*np.array(self.dims)
        for i in range(len(self.detector)):
            self.imv[i].setImage(temp[i].T, pos=self.pos, scale=self.accuracy)

    def reject_outliers(self, data, m=2):
        try:
            return data[abs(data - np.median(data)) < m * np.std(data)]
        except:
            return data

    def func_scan(self):
        temp = self.get_data()
        self.data = temp
        #temp = np.random.normal(size=(200, 200))
        for i in range(len(self.detector)):
            if type(temp[i])==type(False) and temp==0:
                pass
            else:
                self.pos = np.array(self.center)-0.5*np.array(self.dims)
                self.imv[i].setImage(np.nan_to_num(self.data[i].T), pos=self.pos, scale=self.accuracy, autoLevels=False)
                #data_wol = self.reject_outliers(temp[i][~np.isnan(temp[i])].flatten())
                self.imv[i].setLevels(np.nanmin(self.data[i]), np.nanmax(self.data[i]))
                done = np.count_nonzero(np.isnan(self.data))
                not_done = np.count_nonzero(~np.isnan(self.data))
                total = done+not_done

                self.parent.main.Controler_BusyLabel.setText("%s %%"%(int(done/total*100)))


    def monitor(self):
        self.plotwidget = pg.PlotWidget()
        self.lineplot = self.plotwidget.plot()
        labelStyle = {'color': '#FFF', 'font-size': '16px'}
        self.plotwidget.plotItem.setLabel('left', self.ylabel, units=self.yunit,**labelStyle)
        self.plotwidget.plotItem.setLabel('bottom', self.xlabel, units=self.xunit,**labelStyle)
        self.MplAnimate.setCentralWidget(self.plotwidget)
        self.text = pg.TextItem(html='', anchor=(-0.3,1.3), border='w', fill=(0, 0, 255, 100))
        self.plotwidget.plotItem.addItem(self.text)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.monitor_plot)
        self.timer.start(100)
        return self.timer

    def animate_plot(self):
        self.plotwidget = []
        self.lineplot = []
        for i in range(len(self.detector)):
            self.plotwidget.append(pg.PlotWidget())
            self.plotwidget[i].getPlotItem().setTitle(title = self.detector[i].properties['Name'])
            self.lineplot.append(self.plotwidget[i].plot())
            labelStyle = {'color': '#FFF', 'font-size': '16px'}
            self.plotwidget[i].plotItem.setLabel('left', self.ylabel[i], units=self.yunit[i],**labelStyle)
            self.plotwidget[i].plotItem.setLabel('bottom', self.xlabel, units=self.xunit,**labelStyle)

        self.form_widget = FormWidget(None,self.plotwidget)
        self.MplAnimate.setCentralWidget(self.form_widget)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.func_plot)
        self.timer.start(100)
        return self.timer

    def animate_1dscan(self):
        self.plotwidget = []
        self.lineplot = []
        for i in range(len(self.detector)):
            self.plotwidget.append(pg.PlotWidget())
            self.plotwidget[i].getPlotItem().setTitle(title = self.detector[i].properties['Name'])
            self.lineplot.append(self.plotwidget[i].plot())
            labelStyle = {'color': '#FFF', 'font-size': '16px'}
            self.plotwidget[i].plotItem.setLabel('left', self.ylabel[i], units=self.yunit[i],**labelStyle)
            self.plotwidget[i].plotItem.setLabel('bottom', self.xlabel, units=self.xunit,**labelStyle)

        self.form_widget = FormWidget(None,self.plotwidget)
        self.MplAnimate.setCentralWidget(self.form_widget)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.scan_plot1d)
        self.timer.start(100)
        return self.timer

    def animate_scan(self):
        #import pyqtgraph.multiprocess as mp
        #proc = mp.QtProcess()
        #rpg = proc._import('pyqtgraph')
        self.adw.start_scan_dynamic(self.detector,self.devs,self.center,self.dims,self.accuracy,self.speed)
        self.imv = []
        self.vLine = []
        self.hLine = []
        for i in range(len(self.detector)):
            plt = pg.PlotItem(title = self.detector[i].properties['Name'],labels={'bottom': (self.xlabel,self.xunit), 'left': (self.ylabel,self.yunit)})
            self.imv.append(pg.ImageView(view=plt))

            gnuplot = {'ticks': [(0.0, (0, 0, 0, 255)), (0.2328863796753704, (32, 0, 129, 255)), (0.8362738179251941, (255, 255, 0, 255)), (0.5257586450247, (255, 0, 0, 255)), (1.0, (255, 255, 255, 255))], 'mode': 'rgb'}
            self.imv[i].ui.histogram.gradient.restoreState(gnuplot)

            self.vLine.append(pg.InfiniteLine(angle=90, movable=False))
            self.hLine.append(pg.InfiniteLine(angle=0, movable=False))
            self.linePos = {self.xlabel:0,self.ylabel:0}
            self.imv[i].imageItem.scene().sigMouseMoved.connect(self.mouseMoved)
            self.imv[i].getView().addItem(self.vLine[i], ignoreBounds=True)
            self.imv[i].getView().addItem(self.hLine[i], ignoreBounds=True)
            if not i==0:
                self.imv[i-1].getImageItem().getViewBox().setXLink(self.imv[i].getImageItem().getViewBox())
                self.imv[i-1].getImageItem().getViewBox().setYLink(self.imv[i].getImageItem().getViewBox())

        self.form_widget = FormWidget(None,self.imv)
        self.MplAnimate.setCentralWidget(self.form_widget)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.func_scan)
        self.timer.start(500)
        return self.timer

    def mouseMoved(self,evt):
        pos = evt  ## using signal proxy turns original arguments into a tuple
        if self.imv[0].imageItem.sceneBoundingRect().contains(pos) and self.MplAnimate.key==QtCore.Qt.Key_Control:
            mousePoint = self.imv[0].imageItem.mapFromScene(pos)
            self.linePos[self.xlabel] = mousePoint.x()*self.accuracy[0] + self.pos[0]
            self.linePos[self.ylabel] = mousePoint.y()*self.accuracy[1] + self.pos[1]
            for i in range(len(self.hLine)):
                self.hLine[i].setPos(self.linePos[self.ylabel])
                self.vLine[i].setPos(self.linePos[self.xlabel])


class FormWidget(QtGui.QWidget):
    def __init__(self, parent,graphs):
        super(FormWidget, self).__init__(parent)
        self.layout = QGridLayout(self)

        dim = np.ceil(np.sqrt(len(graphs)))
        grid = np.arange(dim*np.ceil(len(graphs)/dim)).reshape(-1,dim)
        for k in range(len(graphs)):
            i,j = np.where(grid==k)
            self.layout.addWidget(graphs[k],i,j)
