"""
scantools.ui.powermeter

A tool to read out the Newport 1830c power meter and display the value.
"""

from PyQt4 import QtGui

from ._powermeter_ui import Ui_PowermeterWindow
from ..devices.powermeter import PowerMeterHost

class PowerMeterWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        self._closing = False

        self.ui = Ui_PowermeterWindow()
        self.ui.setupUi(self)

        self.ui.txtLambda.setEnabled(False)
        self.ui.btnChart.setEnabled(False)
        self.ui.chkAttn.setEnabled(False)
        self.ui.lcdPower.setSegmentStyle(QtGui.QLCDNumber.Outline)

        self._wl = None

        self._pm = PowerMeterHost()
        self._pm.updated.connect(self.updateUi)
        self._pm.connected.connect(self.on_connected)
        self._pm.disconnected.connect(self.on_disconnected)
        self._pm.device_exception.connect(self.on_error)
        self._pm.timeout_warning.connect(self.on_timeout)

        self.ui.btnConnect.clicked.connect(self.do_connect)
        self.ui.txtLambda.returnPressed.connect(self.setWavelength)

        self.statuslabel = QtGui.QLabel('Not connected')
        self.ui.statusbar.addPermanentWidget(self.statuslabel, 1)

    def updateUi(self):

        if self._wl != self._pm.wavelength:
            self.ui.txtLambda.setText(str(self._pm.wavelength))
            self._wl = self._pm.wavelength

        p_mW = self._pm.power / 1e-3
        if p_mW >= 1:
            self.ui.lcdPower.display(('%.3f' % p_mW)[:5])
            self.ui.lblUnit.setText('mW')
        elif 0.095 <= p_mW < 1:
            self.ui.lcdPower.display('%05.1f' % (p_mW / 1e-3))
            self.ui.lblUnit.setText('µW')
        elif p_mW > 0.009:
            self.ui.lcdPower.display('%05.2f' % (p_mW / 1e-3))
            self.ui.lblUnit.setText('µW')
        else:
            self.ui.lcdPower.display('%05.3f' % (p_mW / 1e-3))
            self.ui.lblUnit.setText('µW')
        self.ui.lcdPower.setSegmentStyle(QtGui.QLCDNumber.Flat)

    def setWavelength(self):
        try:
            wl = float(self.ui.txtLambda.text())
            self._pm.set_wavelength(wl)
        except ValueError:
            pass

    def on_connected(self):
        self.statuslabel.setText('Connected')
        self.ui.btnConnect.setText("Disconnect")
        self.ui.btnConnect.clicked.disconnect(self.do_connect)
        self.ui.btnConnect.clicked.connect(self.do_disconnect)
        self.ui.txtLambda.setEnabled(True)

    def on_disconnected(self):
        self.statuslabel.setText('Disconnected')
        self.ui.btnConnect.setText("Connect")
        self.ui.btnConnect.clicked.disconnect(self.do_disconnect)
        self.ui.btnConnect.clicked.connect(self.do_connect)
        self.ui.txtLambda.setEnabled(False)
        self.ui.lcdPower.setSegmentStyle(QtGui.QLCDNumber.Outline)

        if self._closing:
            self.close()

    def do_connect(self):
        self._pm.connect_to_device()

    def do_disconnect(self):
        self._pm.disconnect_from_device()

    def on_error(self, exc):
        msgbox = QtGui.QMessageBox(self)
        msgbox.setWindowTitle('Error')
        msgbox.setText(str(exc))
        msgbox.show()

    def on_timeout(self):
        self.ui.lcdPower.setSegmentStyle(QtGui.QLCDNumber.Outline)
        #self.ui.statusbar.showMessage('WARNING: TIMEOUT', 1000)

    def closeEvent(self, ev):
        if self._pm.get_is_connected():
            self.do_disconnect()
            self.statuslabel.setText('Disconnecting from device...')
            self._closing = True
            ev.ignore()



if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    powermeter_window = PowerMeterWindow()
    powermeter_window.show()
    sys.exit(app.exec_())

