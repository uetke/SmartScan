"""lib.app

A central object that binds the application together where needed.
"""

from collections import namedtuple

from PyQt4.QtCore import QObject, pyqtSignal

from .db_comm import db_comm

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
        self._app.boom.emit()
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
    boom = pyqtSignal()

    def __new__(cls):
        if cls._INSTANCE is None:  
            cls._INSTANCE = QObject.__new__(cls)
            cls._INSTANCE._init()
        return cls._INSTANCE

    def __init__(self):
        pass

    def _init(self):
        QObject.__init__(self)

        self._session = {}
        self._logbook = self.db = db_comm('_private/logbook.db')

        self._session['db'] = self._logbook

        self.last_logentry = None

    @property
    def logbook(self):
        return self._logbook

    @property
    def session(self):
        return self._session
    