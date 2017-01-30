"""
Software interface to shutters and flippers
"""

import contextlib
import copy
from enum import IntEnum
import logging
#import threading
import time

import numpy as np
from PyQt4 import QtCore

import devices.flipper
from lib.config import DeviceConfig, VARIABLES
from ..app import ScanApplication

_logger = logging.getLogger(__name__)

class ShutterService(QtCore.QObject):
    """
    Provides access to shutters and flippers configured.

    This should NOT be initialized directly by other components. 
    Use ScanApplication.get_service() to acquire a reference to it.
    """

    any_state_changed = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self._app = ScanApplication()

        self.init_adwin_shutters()
        self.init_thorlabs_flippers()

        self._polling_thread = QtCore.QThread()
        self._polling_worker = ShutterService.PollingWorker(self)
        self._polling_worker.moveToThread(self._polling_thread)
        self._polling_thread.started.connect(self._polling_worker.start_timer)
        self._polling_thread.start()

        self._app.shutting_down.connect(self.close)

    def init_adwin_shutters(self):
        # find shutter configurations
        try:
            shutter_cfg = DeviceConfig(type='Adwin', type_name='Digital')
        except ValueError:
            # no digital outputs configured at all!
            return

        shutter_properties = None
        if isinstance(shutter_cfg.properties, list):
            shutter_properties = [p for p in shutter_cfg.properties if 'Shutter' in p]
        elif 'Shutter' in shutter_properties:
            shutter_properties = [shutter_cfg.properties]

        if not shutter_properties:
            return

        self._adwin = self._app.get_adwin()

        self._adwin.set_par(VARIABLES['par']['shutter_button_mask'], 0)
        self._adwin.set_datalong(np.array([-1]), VARIABLES['data']['protection_shutter_params'])
        self._shutters = [Shutter(self, p) for p in shutter_properties]
        for s in self._shutters:
            def shutter_changed_slot(shutter=s):
                self.any_state_changed.emit(shutter)
            s.changed_state.connect(shutter_changed_slot)

        # Check if the shutter monitoring process is needed
        if (self._adwin.get_par(VARIABLES['par']['shutter_button_mask']) or
            self._adwin.get_data(VARIABLES['data']['protection_shutter_params'], 1)[0] > 0):

            self._adwin.load_portable('shutters.Tx4')
            self._adwin.start(4)  # shutter process
            self._adwin.start(10) # monitor process, required by shutters

    def init_thorlabs_flippers(self):
        try:
            flipper_cfg = DeviceConfig(type='USB', type_name='ThorlabsFlipper')
        except ValueError:
            # no flippers configured
            return

        if isinstance(flipper_cfg.properties, list):
            flipper_properties = flipper_cfg.properties
        else:
            flipper_properties = [flipper_cfg.properties]

        self._flippers = []#[ThorlabsFlipper(self, p) for p in flipper_properties]
        for p in flipper_properties:
            try:
                f = ThorlabsFlipper(self, p)
            except IOError:
                _logger.warning('Failed to initialize flipper: {}'.format(p['Name']))
            else:
                self._flippers.append(f)
                def flipper_changed_slot(flipper=f):
                    self.any_state_changed.emit(flipper)
                f.changed_state.connect(flipper_changed_slot)

    def _get_adwin_digout_status(self):
        return self._adwin.get_par(VARIABLES['par']['digout_status'])

    @property
    def devices(self):
        return self._shutters + self._flippers

    @property
    def shutters(self):
        return self._shutters

    @property
    def flippers(self):
        return self._flippers

    def get_shutter(self, name):
        for s in self._shutters:
            if s.name == name:
                return s
        raise RuntimeError('Shutter not found')

    def get_flipper(self, name):
        for f in self._flippers:
            if f.name == name:
                return f
        raise RuntimeError('Flipper not found')

    class PollingWorker(QtCore.QObject):
        def __init__(self, service, interval=200):
            super().__init__()
            self._service = service
            self._polling_interval = interval

        def timerEvent(self, ev):
            if self._service._shutters:
                shutter_status = self._service._get_adwin_digout_status()
                for s in self._service._shutters:
                    s._poll2(shutter_status)

            for f in self._service._flippers:
                f._poll()

        def start_timer(self):
            self._timer = QtCore.QBasicTimer()
            self._timer.start(self._polling_interval, self)

    def close(self):
        if self._polling_thread.isRunning():
            self._polling_thread.exit()
            self._polling_thread.wait()

    def __del__(self):
        self.close()


class Shutter(QtCore.QObject):
    """
    Class representing a shutter connected to an ADwin digital output
    """

    changed_state = QtCore.pyqtSignal()

    def __init__(self, service, shutter_props):
        super().__init__()

        self._shutter_service = service

        self.name = shutter_props['Name']
        self.description = shutter_props['Description']
        self._port = shutter_props['Output']['Hardware']['PortID'] - 1
        self._open_state = shutter_props['Shutter'].get('open-state', 1)

        self.shutter_type = 'Shutter'

        if 'Laser' in shutter_props['Shutter']:
            self.shutter_type = 'Laser Shutter'
            self.laser_info = Laser(shutter_props['Shutter']['Laser'])
        else:
            self.laser_info = None

        if 'Protection' in shutter_props['Shutter']:
            self.shutter_type = 'Protective Shutter'
            # configure the ADwin process
            dev_name = shutter_props['Shutter']['Protection']['device-name']
            threshold = shutter_props['Shutter']['Protection']['threshold']
            dev_port = DeviceConfig(dev_name)['Input']['Hardware']['PortID']

            cfg_array = service._adwin.get_data(VARIABLES['data']['protection_shutter_params'], 48)
            for i in range(0, 16*3, 3):
                if cfg_array[i] <= 0:
                    cfg_array[i] = dev_port
                    cfg_array[i+1] = int(threshold)
                    cfg_array[i+2] = self._port
                    cfg_array[i+3] = -1
                    break
                else:
                    continue
            service._adwin.set_datalong(cfg_array, VARIABLES['data']['protection_shutter_params'], 48)

        if shutter_props['Shutter'].get('has-button', False):
            my_bit = 1 << self._port
            mask = service._adwin.get_par(VARIABLES['par']['shutter_button_mask'])
            mask |= my_bit
            self._adwin.set_par(VARIABLES['par']['shutter_button_mask'], mask)

        self._last_known_state = self.state

    @property
    def state(self):
        digout_word = self._shutter_service._get_adwin_digout_status()
        digout_bit = digout_word & (1 << self._port)
        if bool(digout_bit) == self._open_state:
            return ShutterState.OPEN
        else:
            return ShutterState.CLOSED

    @state.setter
    def state(self, new_state):
        if self.state == new_state:
            return

        # check for conflicts with flippers
        for flipper in self._shutter_service.flippers:
            try:
                flipper.state.check_conflicts()
            except ShutterConflict.Violation:
                raise ShutterConflict.Violation(flipper.name)

        new_bit = (int(new_state) ^ (~self._open_state)) & 1
        if new_bit:
            self._shutter_service._adwin.set_digout(self._port)
        else:
            self._shutter_service._adwin.clear_digout(self._port)

        self._last_known_state = new_state
        self.changed_state.emit()

    def _poll(self):
        new_state = self.state
        if self._last_known_state != new_state:
            self.changed_state.emit()
            self._last_known_state = new_state

    def _poll2(self, digout_word):
        digout_bit = digout_word & (1 << self._port)
        new_state = ShutterState.OPEN if bool(digout_bit) == self._open_state else ShutterState.CLOSED
        if self._last_known_state != new_state:
            self.changed_state.emit()
            self._last_known_state = new_state

    def open(self):
        self.state = ShutterState.OPEN

    def close(self):
        self.state = ShutterState.CLOSED

    def __str__(self):
        return '{}: {} (port {}) - {}'.format(self.shutter_type, self.name,
                                              self._port + 1, self.state.name)

    def __repr__(self):
        return '<{}>'.format(str(self))

class ShutterState(IntEnum):
    OPEN = 1
    CLOSED = 0

class Laser:
    """
    Encapsulated the properties of a shutter-controlled laser
    """
    def __init__(self, properties):
        self.name = str(properties['name'])
        if 'wavelength' in properties:
            self.wavelength = float(properties['wavelength'])
        else:
            self.wavelength = None


    def __str__(self):
        if self.wavelength is not None:
            return 'Laser: {} ({} nm)'.format(self.name, self.wavelength)
        else:
            return 'Laser: {}'.format(self.name)

    def __repr__(self):
        return '<{}>'.format(str(self))


class ThorlabsFlipper(QtCore.QObject):
    """
    Class handling a Thorlabs USB flipper device
    """

    changed_state = QtCore.pyqtSignal()

    def __init__(self, service, properties):
        super().__init__()

        self._shutter_service = service

        self.name = properties['Name']
        self.description = properties['Description']

        self.serial_number = str(properties['Hardware']['SerialNum']).encode('ascii')
        self._device = devices.flipper.Flipper(self.serial_number)

        self._device.initializeHardwareDevice()

        # Get configured states
        self.states = []
        self._states = {}
        # There are always two states!!
        assert isinstance(properties['Flipper']['State'], list)
        for state_properties in properties['Flipper']['State']:
            pos = state_properties['Position']
            state_object = FlipperState(pos, str(state_properties['Name']))
            self.states.append(state_object)
            self._states[pos] = state_object
            # set up any conflict definitions there may be
            if 'Conflict' in state_properties:
                conflicts = state_properties['Conflict']
                if isinstance(conflicts, dict):
                    conflicts = [conflicts]
                for conflict_def in conflicts:
                    state_object.add_conflict(ShutterConflict(
                        self._shutter_service, conflict_def))

        # If there are restrictions in place while switching, load them!
        self._switching_conflicts = []
        if 'While-Switching' in properties['Flipper']:
            conflicts = properties['Flipper']['While-Switching']['Conflict']
            if isinstance(conflicts, dict):
                conflicts = [conflicts]
            for conflict_def in conflicts:
                self._switching_conflicts.append(ShutterConflict(
                    self._shutter_service, conflict_def))

        self._last_known_state = self.state

    def __str__(self):
        return 'ThorLabs Flipper: {} (s/n {})'.format(self.name, self.serial_number)

    def __repr__(self):
        return '<{}>'.format(str(self))

    @property
    def state(self):
        pos = self._device.getPos()
        return self._states.get(pos)

    @state.setter
    def state(self, newpos):
        # Check for conflicts arising in the new state (may raise exception)
        new_state = self._states[newpos]
        new_state.check_conflicts()

        # if any shutters need closing during the switch, do it!
        stack = contextlib.ExitStack()
        for conflict in self._switching_conflicts:
            stack.enter_context(conflict.evade())

        # we'll undo that once the switch is done!
        def slot_statechanged():
            if self.state == new_state:
                stack.close()
                self.changed_state.disconnect(slot_statechanged)
        self.changed_state.connect(slot_statechanged, QtCore.Qt.DirectConnection)

        # now that we're safe, switch
        self._device.goto(newpos)

    def _poll(self):
        new_state = self.state
        if self._last_known_state != new_state:
            self.changed_state.emit()
            self._last_known_state = new_state

    def __del__(self):
        self._device.close()

class FlipperState(int):
    def __new__(cls, value, name):
        self = super(FlipperState, cls).__new__(cls, value)
        self._name = name
        self._conflicts = []
        return self

    @property
    def name(self):
        return self._name

    @property
    def conflicts(self):
        return copy.copy(self._conflicts)

    def add_conflict(self, conflict):
        self._conflicts.append(conflict)

    def check_conflicts(self):
        for c in self._conflicts:
            c.check()

    def __str__(self):
        return 'FlipperState: {} ({:d})'.format(self.name, self)

    def __repr__(self):
        return '<{}>'.format(str(self))


class ShutterConflict:
    def __init__(self, service, conflict_def):
        self._shutter_service = service
        if conflict_def['Type'] != 'Shutter':
            raise NotImplementedError('unknown conflict type')

        shutter_name = conflict_def['Name']
        # find the shutter!
        self._shutter = self._shutter_service.get_shutter(shutter_name)

    def check(self):
        if self._shutter.state == ShutterState.OPEN:
            raise ShutterConflict.Violation(self._shutter.name)

    @contextlib.contextmanager
    def evade(self):
        old_state = self._shutter.state
        self._shutter.state = ShutterState.CLOSED
        yield
        print ('yes, end evade!')
        self._shutter.state = old_state


    def Violation(RuntimeError):
        pass

