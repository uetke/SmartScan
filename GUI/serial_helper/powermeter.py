"""
GUI.serial_helper.powermeter

A tool to read out the Newport 1830c power meter and display the value.
"""

import sys
import time

from PyQt4 import QtCore, QtGui
from pyvisa.errors import VisaIOError, VI_ERROR_TMO

from devices import powermeter1830c
from lib.config import DeviceConfig

from ._powermeter_ui import Ui_PowermeterWindow

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

class PowerMeterHost(QtCore.QObject):

    updated = QtCore.pyqtSignal()
    connected = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()
    device_exception = QtCore.pyqtSignal(Exception)
    timeout_warning = QtCore.pyqtSignal()

    def __init__(self, powermeter_cfg=None):
        super().__init__()
        if powermeter_cfg is None:
            powermeter_cfg = DeviceConfig('Powermeter', 'Serial')
        
        self._device_cfg = powermeter_cfg
        self._device = None
        self._worker = None

    def connect_to_device(self):
        self._device = powermeter1830c.PowerMeter1830c(self._device_cfg['Hardware']['PortID'])
        f = self._device.initialize_async()
        self._worker = PowerMeterHost.Worker(self, self._device, f, 0.2)
        self._worker.start()

    def disconnect_from_device(self):
        if self._worker is not None:
            self._worker._keep_connection = False

    def destroyed(self):
        self.disconnect_from_device()

    def set_wavelength(self, wl):
        self._worker._new_wavelength = wl
    
    def get_is_connected(self):
        return self._device is not None

    class Worker(QtCore.QThread):
        def __init__(self, host, device, init_future, interval):
            super().__init__()
            self._h = host
            self._device = device
            self._init_future = init_future
            self._interval = interval
            self._keep_connection = True
            self._new_wavelength = None

        def run(self):
            # Wait for the initialization to complete.
            exc = self._init_future.exception()
            if exc is not None:
                self._h.device_exception.emit(exc)
                # remove references to self
                self._h._worker = None
                self._h._device = None
                return

            try:

                self._device.units = 'Watts'
                self._device.lockout = True
                self._h.connected.emit()

                while self._keep_connection:
                    # do stuff
                    try:
                        if self._new_wavelength is not None:
                            self._device.wavelength = self._new_wavelength
                            self._new_wavelength = None
                        self._h.wavelength = self._device.wavelength
                        self._h.attn = self._device.attenuator
                        self._h.power = self._device.data

                        self._h.updated.emit()
                    except VisaIOError as err:
                        if err.error_code == VI_ERROR_TMO:
                            self._h.timeout_warning.emit()
                        else:
                            raise

                    time.sleep(self._interval)

                self._device.lockout = False

            except Exception as err:
                self._h.device_exception.emit(err)

            finally:
                self._device.finalize()
                self._h.disconnected.emit()

                # remove references to self
                self._h._worker = None
                self._h._device = None



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    powermeter_window = PowerMeterWindow()
    powermeter_window.show()
    sys.exit(app.exec_())
