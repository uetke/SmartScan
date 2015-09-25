from pyqtgraph.Qt import QtCore, QtGui
import _session

class ConfigWindow(QtGui.QWidget):
    """ Simple class to change the values for the acquisition times.
    """
    def __init__(self,parent=None):
        tt = _session.time
        acc = _session.accuracy
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Configure the times')
        self.setGeometry(30,30,100,100)
        self.layout = QtGui.QGridLayout(self)

        self.time_label = QtGui.QLabel(self)
        self.time_label.setText('Time (s): ')
        self.time = QtGui.QLineEdit(self)
        self.time.setText(str(tt))
        self.accuracy_label = QtGui.QLabel(self)
        self.accuracy_label.setText('Accuracy (ms): ')
        self.accuracy = QtGui.QLineEdit(self)
        self.accuracy.setText(str(acc*1000))

        self.apd_time_label = QtGui.QLabel(self)
        self.apd_time_label.setText('APD Time (s): ')
        self.apd_time = QtGui.QLineEdit(self)
        self.apd_time.setText(str(_session.apdtime))
        self.apd_accuracy_label = QtGui.QLabel(self)
        self.apd_accuracy_label.setText('APD Accuracy (us): ')
        self.apd_accuracy = QtGui.QLineEdit(self)
        self.apd_accuracy.setText(str(_session.apdacc*1000000))

        self.contin_runs = QtGui.QCheckBox('Continuous runs', self)
        self.contin_runs.setChecked(True)

        self.apply_button = QtGui.QPushButton('Apply', self)
        self.apply_button.clicked[bool].connect(self.SetTimes)

        self.run_button = QtGui.QPushButton('Run', self)

        self.layout.addWidget(self.time_label,0,0)
        self.layout.addWidget(self.time,0,1)
        self.layout.addWidget(self.accuracy_label,1,0)
        self.layout.addWidget(self.accuracy,1,1)
        self.layout.addWidget(self.apd_time_label,2,0)
        self.layout.addWidget(self.apd_time,2,1)
        self.layout.addWidget(self.apd_accuracy_label,3,0)
        self.layout.addWidget(self.apd_accuracy,3,1)
        self.layout.addWidget(self.contin_runs,4,0)
        self.layout.addWidget(self.apply_button,5,0,1,2)
        self.layout.addWidget(self.run_button,6,0,1,2)

    def SetTimes(self):
        new_time = float(self.time.text())
        new_accuracy = float(self.accuracy.text())/1000
        new_apd_time = float(self.apd_time.text())
        new_apd_accuracy = float(self.apd_accuracy.text())/1000000
        _session.time = new_time
        _session.accuracy = new_accuracy
        _session.apdtime = new_apd_time
        _session.apdacc = new_apd_accuracy
        _session.runs = self.contin_runs.isChecked()
        self.emit( QtCore.SIGNAL('Times'), new_time, new_accuracy, _session.runs)
