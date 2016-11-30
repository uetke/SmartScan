"""
scantools.devices.powermeter

Host object handling interactions with the Newport 1830c power meter.
"""

import time

from PyQt4 import QtCore
from pyvisa.errors import VisaIOError, VI_ERROR_TMO

from devices import powermeter1830c
from lib.config import DeviceConfig


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
