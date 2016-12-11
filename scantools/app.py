"""scantools.app

A central object that binds the application together where needed.
"""

from collections import namedtuple
from functools import wraps
from importlib import import_module
import logging
import os.path
import sys
import xml.etree.ElementTree as ET

from PyQt4.QtCore import QObject, pyqtSignal

from lib.db_comm import db_comm
from lib import config
from lib.logger import get_all_caller

__all__ = ['ScanApplication', 'LogEntry']

class LogEntry(QObject):
    """
    Represents an entry in the logbook, whether saved or not.
    Different components of the application can add information to the entry
    until it is saved.
    """

    _metadatum = namedtuple('_metadatum', ['component', 'key', 'value'])

    def __init__(self):
        super().__init__()
        self._in_db = False
        self._app = ScanApplication()

        self.user_id = self._app.session.get('userId')
        self.setup_id = self._app.session.get('setupId')
        self.entry_type = None
        self.file_name = None
        self.detectors = None
        self.variables = None
        self.comments = None

        self._metadata = []

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if self._in_db and name in {'user_id', 'setup_id', 'entry_type', 'file_name',
                                    'detectors', 'variables', 'comments'}:
            self.commit()

    @property
    def metadata(self):
        return self._metadata[:]

    def announce(self):
        """
        signal the creation of this log entry
        """
        self._app.new_logentry.emit(self)
        self._app.last_logentry = self

    def add_metadatum(self, component, key, value):
        datum = LogEntry._metadatum(component, key, value)
        self._metadata.append(datum)
        if self._in_db:
            self._save_metadatum(datum)

    def commit(self):
        db = self._app.logbook

        entry = {
            'user': self.user_id,
            'setup': self.setup_id,
            'entry': self.entry_type,
            'file': self.file_name,
            'detectors': self.detectors,
            'variables': self.variables,
            'comments': self.comments
        }

        if self._in_db:
            db.update_entry(self._rowid, entry)
        else:
            self._rowid = db.new_entry(entry)
            self._in_db = True

            for md in self._metadata:
                self._save_metadatum(md)

    def _save_metadatum(self, datum):
        db = self._app.logbook
        db.add_metadata_to_entry(self._rowid, *datum)


class ScanApplication(QObject):
    """
    Singleton application object
    """

    _INSTANCE = None

    new_logentry = pyqtSignal(object)
    shutting_down = pyqtSignal()

    def __new__(cls):
        if cls._INSTANCE is None:  
            cls._INSTANCE = QObject.__new__(cls)
            cls._INSTANCE._init()
        return cls._INSTANCE

    def __init__(self):
        pass

    def _init(self):
        QObject.__init__(self)
        self.logger = logging.getLogger('scantools.app.ScanApplication')

        self._session = {}
        self._logbook = self.db = db_comm('_private/logbook.db')
        self.project_root = os.path.dirname(os.path.dirname(__file__))

        self._session['db'] = self._logbook

        self._session['dev_conf'] = None

        self._adwin_booted = False

        self.last_logentry = None

        self._load_apps_xml()

    @property
    def logbook(self):
        return self._logbook

    @property
    def session(self):
        return self._session

    def _load_apps_xml(self):
        """Load config/apps.xml"""
        apps_xml = ET.parse(config.open_configfile("apps.xml"))

        apps_root = apps_xml.getroot()

        # Load driver hosts
        self.devices = []
        for driver_tag in apps_root.iterfind('./hosts/driver-host'):
            group = driver_tag.get('group')
            type_ = driver_tag.get('type')
            try:
                device_cfg = config.DeviceConfig(type=group, type_name=type_)
            except ValueError:
                self.logger.debug("No {} device of type {} configured."
                                  .format(group, type_))
            else:
                try:
                    if len(device_cfg) == 1:
                        self.devices.append(
                            DriverHostHandler(driver_tag, device_cfg.properties))
                    else:
                        for p in device_cfg.properties:
                            self.devices.append(DriverHostHandler(driver_tag, p))
                except (ValueError, ImportError, AttributeError):
                    self.logger.warn('Failed to load driver for {}'.format(type_),
                                     exc_info=sys.exc_info())

        # Load non-driver services
        self._available_services = {}
        self._active_services = {}
        for service_tag in apps_root.iterfind('./services/service'):
            class_name = service_tag.get('class')
            try:
                module_name, class_basename = class_name.rsplit('.', 1)
                module = import_module(module_name)
                service_class = getattr(module, class_basename)
                self._available_services[class_name] = service_class
                if service_tag.get('autostart') in {'true', 'True', 'yes', '1'}:
                    self._active_services[class_name] = service_class()
                    self.logger.info('Autostarted service {}'.format(class_name))
            except:
                self.logger.warn('Failed to load service {}'.format(class_name),
                                 exc_info=sys.exc_info())

        # Load UI modules
        self.scan_tools = []
        for app_tag in apps_root.iterfind('./user-interfaces/application'):
            try:
                self.scan_tools.append(ScanTool(app_tag))
            except RuntimeError:
                self.logger.info('Application {} is unavailable on this system.'.format(
                    app_tag.get('name')))
            except (ValueError, ImportError, AttributeError):
                self.logger.info('Failed to configure application {}'.format(
                    app_tag.get('name')))

    def get_devices(self, device_or_class):
        """
        Returns drivers for all available devices matching the argument.
        This can be:
         * The driver class
         * The driver class' full name (including module)
         * The device type
         * The device name
        Always returns a list. (May only have one item or be empty)
        """
        is_str = isinstance(device_or_class, str)
        matches = []
        for device in self.devices:
            if is_str:
                if device_or_class in (device.name,
                                       device.type_,
                                       device.driver_class_name):
                    matches.append(device.get())
            elif device.driver_class == device_or_class:
                matches.append(device.get())

        return matches

    def get_service(self, name_or_class):
        """
        Returns an instance of the requested service. Raises RuntimeError if the
        service is not known, or for non-autostart services any error occurring
        during service startup.

        The argument can be:
         * The service class
         * The full name of the service class (including module)
         * The name of the service class (not including the module)
        """
        if name_or_class in self._active_services:
            return self._active_services[name_or_class]

        for name, obj in self._active_services.items():
            basename = name.rsplit('.', 1)[-1]
            if name_or_class in (basename, type(obj)):
                return obj

        service_class = self._available_services.get(name_or_class)
        if service_class is None:
            for name, cls in self._available_services.items():
                basename = name.rsplit('.', 1)[-1]
                if name_or_class in (basename, cls):
                    service_class = cls
                    class_name = name
                    break
            else:
                raise RuntimeError("No such service: {}".format(name_or_class))
        else:
            class_name = name_or_class

        self._active_services[class_name] = service_class()
        self.logger.info('Started service {}'.format(class_name))
        return self._active_services[class_name]

    def get_scantool(self, name_or_class):
        """
        Returns the ScanTool identified by the argument
        """
        for st in self.scan_tools:
            if (name_or_class == st.name or 
                (hasattr(st, "class_name") and name_or_class == st.class_name) or
                (hasattr(st, "window_class") and name_or_class == st.window_class)):
                return st

    def get_adwin(self):
        if not self._adwin_booted:
            self.boot_adwin()
        return self._adwin

    def boot_adwin(self, *, force=False):
        from lib.adq_mod import adq

        if self._adwin_booted and not force:
            raise RuntimeError("Adwin is already booted!")

        adwin_info = config.DeviceConfig.get_adwin_info()
        model = adwin_info['model']
        dev_num = int(adwin_info['device_number'])
        self._adwin = adq(dev_num, model)
        if self._adwin.adw.Test_Version() != 0: 
            self._adwin.boot()
            self.logger.info('Booting the ADWin...')
        if model == 'gold':
            self._adwin.init_port7() # This comes from the UberScan era. Is it still needed?
        self._adwin.load_portable('init_adwin.Tx8')
        self._adwin.start(8)
        self._adwin.wait(8)
        self._adwin.load_portable('monitor.Tx0')
        self._adwin.load_portable('atomic_rw.Tx6')
        self._adwin.load_portable('adwin.Tx9')

        self._adwin_booted = True


class DriverHostHandler:
    def __init__(self, driver_xml, device_xml_dict):
        self.group = driver_xml.get('group')
        self.type_ = driver_xml.get('type')
        self.description = driver_xml.get('description')
        self.object_mode = driver_xml.get('object-mode', 'multiple')
        if self.object_mode == 'one-per-device':
            self._DRIVER_INSTANCE = None

        if self.object_mode not in ('one-per-device', 'multiple'):
            raise ValueError('Unknown object mode: "{}"'.format(self.object_mode))

        self.driver_class_name = driver_xml.get('class')
        module_name, class_name = self.driver_class_name.rsplit('.', 1)
        module = import_module(module_name)
        self.driver_class = getattr(module, class_name)

        self.device_config = device_xml_dict
        self.name = device_xml_dict['Name']

    def __str__(self):
        if self.description is not None:
            return 'Driver: ' + self.description
        else:
            return 'Driver for ' + self.type_

    def __repr__(self):
        return '<{}>'.format(str(self))


    def get(self):
        if self.object_mode == 'one-per-device':
            if self._DRIVER_INSTANCE is None:
                self._DRIVER_INSTANCE = self.driver_class(self.device_config)
            return self._DRIVER_INSTANCE
        else:
            return self.driver_class(self.device_config)

class ScanTool(QObject):
    """
    Class that knows how to launch utility programs
    """

    launched = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, app_xml):
        super().__init__()
        self.name = app_xml.get('name')
        self.description = app_xml.get('description')
        self.launch_mode = app_xml.get('launch-mode')
        self.logger = logging.getLogger('scantools.app.ScanTool')

        if self.launch_mode == 'QMainWindow':
            self.class_name = app_xml.get('class')
            module_name, class_name = self.class_name.rsplit('.', 1)
            module = import_module(module_name)
            self.window_class = getattr(module, class_name)
            self._window = None
        elif self.launch_mode == 'flask':
            self.blueprint_name = app_xml.get('blueprint')
            module_name, blueprint_name = self.blueprint_name.rsplit('.', 1)
            module = import_module(module_name)
            self.blueprint = getattr(module, blueprint_name)
            self._flask_app_host = None
        else:
            raise ValueError('Unsupported launch-mode: {}'.format(self.launch_mode))

        # TODO: check the requirements, boot adwin if needed.
        # also, find a good way to configure the session...

        self._pre_launch = None
        for qualifier_elem in app_xml:
            if qualifier_elem.tag == 'requires-device':
                group = qualifier_elem.get('group', None)
                type_name = qualifier_elem.get('type', None)
                name = qualifier_elem.get('name', None)
                try:
                    config.DeviceConfig(name=name, type=group, type_name=type_name)
                except ValueError:
                    raise RuntimeError('Required device is not configured')
            elif qualifier_elem.tag == 'requires-test':
                test_name = qualifier_elem.get('callable')
                module_name, fn_name = test_name.rsplit('.', 1)
                module = import_module(module_name)
                test_fn = getattr(module, fn_name)
                try:
                    ok = test_fn()
                except:
                    self.logger.warn('Error running test {}!'.format(test_name),
                                     exc_info=sys.exc_info())
                    ok = False
                if not ok:
                    raise RuntimeError('Test failed')
            elif qualifier_elem.tag == 'pre-launch':
                # function to call before launching
                full_fn_name = qualifier_elem.get('callable')
                module_name, fn_name = full_fn_name.rsplit('.', 1)
                module = import_module(module_name)
                self._pre_launch = getattr(module, fn_name)
            elif qualifier_elem.tag == 'requires-service':
                app = ScanApplication()
                service_class_name = qualifier_elem.get('class')
                if service_class_name not in app._available_services:
                    raise RuntimeError('Required service not configured')
            else:
                raise ValueError('Unknown qualifier: <{}/>'.format(qualifier_elem.tag))

    def _show_qmainwindow(self, **kwargs):
        if self._window is None:
            self.set_qmainwindow(self.window_class(kwargs.get('parent_window', None)))
        
            self._window.show()
            self.launched.emit()

    def set_qmainwindow(self, window):
        assert self.launch_mode == 'QMainWindow'

        self._window = window

        closeEventMethod = self._window.closeEvent
        @wraps(closeEventMethod)
        def closeEventPatch(ev):
            closeEventMethod(ev)
            if self._window is window and ev.isAccepted():
                self.closed.emit()
                self._window = None

        self._window.closeEvent = closeEventPatch

    def launch(self, **kwargs):
        if self.launch_mode == 'QMainWindow':
            self._show_qmainwindow(**kwargs)
        elif self.launch_mode == 'flask':
            from .ui import flaskapp
            self._flask_app_host = flaskapp.launch_app(self.name, self.blueprint)
            def on_closed():
                self._flask_app_host = None
                self.closed.emit()
            self._flask_app_host.closed.connect(on_closed)
            self.launched.emit()
            self.logger.info('Started {} tool at {}'.format(self.name, 
                             self._flask_app_host.public_url))


    def is_running(self):
        if self.launch_mode == 'QMainWindow':
            return self._window is not None
        elif self.launch_mode == 'flask':
            return self._flask_app_host is not None

    def __str__(self):
        return 'ScanTool: {}'.format(self.name)

    def __repr__(self):
        return '<{}>'.format(str(self))
