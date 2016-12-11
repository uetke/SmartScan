"""
Code to set up web-based UIs (e.g. the shutter GUI)
"""

HOST = "0.0.0.0"
PORT = 8888

import logging
import threading
import socket

from flask import Flask
from werkzeug.serving import make_server
from PyQt4 import QtCore, QtGui, QtWebKit

from ..app import ScanApplication

_logger = logging.getLogger(__name__)

app = Flask(__name__)

_server = None
_server_thread = None
_running_apps = {}
_active_apps = set()

def launch_app(name, blueprint):
    if name in _running_apps:
        app = _running_apps[name]
    else:
        app = FlaskAppHost(name, blueprint)
        app.start()
    app.show()
    return app

class FlaskAppHost(QtCore.QObject):
    closed = QtCore.pyqtSignal()

    def __init__(self, name, blueprint):
        super().__init__()

        self.name = name
        self.blueprint = blueprint
        self.url_prefix = '/{}'.format(name.lower())

    def start(self):
        global _server, _server_thread

        _active_apps.add(self)

        if self.name in _running_apps:
            return

        app.register_blueprint(self.blueprint, url_prefix=self.url_prefix)

        if _server is None:
            _logger.info("Initializing web server at {}:{}".format(HOST, PORT))
            _server = make_server(HOST, PORT, app, threaded=True)
            _server_thread = ServerThread(_server)
            _server_thread.start()

        _running_apps[self.name] = self

    def show(self):
        self._window = WebWindow(self)
        self._window.show()

    @property
    def url(self):
        return 'http://localhost:{port}{url_prefix}/'.format(
            port=PORT, url_prefix=self.url_prefix)

    @property
    def public_url(self):
        return 'http://{fqdn}:{port}{url_prefix}/'.format(
            fqdn=socket.getfqdn(), port=PORT, url_prefix=self.url_prefix)

    def close(self):
        global app, _server_thread, _server, _running_apps

        _active_apps.remove(self)
        self._window = None

        # was this the last app to quit?
        if not _active_apps:
            # stop serving
            _server_thread.stop_server()
            # reset flask and module state
            app = Flask(__name__)
            _running_apps = {}
            _server = None
            _server_thread = None

        self.closed.emit()


class ServerThread(threading.Thread):
    def __init__(self, server):
        super().__init__()
        self._server = server
        scan_app = ScanApplication()
        scan_app.shutting_down.connect(self.stop_server)

    def run(self):
        _logger.info('Started web server')
        self._server.serve_forever()

    def stop_server(self):
        self._server.server_close()
        self._server.shutdown()

class WebWindow(QtGui.QMainWindow):
    def __init__(self, flaskapp):
        super().__init__()
        self._app = flaskapp

        self._webview = QtWebKit.QWebView(self)
        self.setCentralWidget(self._webview)
        self.setWindowTitle(self._app.name)

        self.resize(360, 480)

        self._webview.load(QtCore.QUrl(self._app.url))

    def closeEvent(self, ev):
        reply = QtGui.QMessageBox.question(self, 'Really Quit?', 
            "You will no longer be able to access this web-based app from other devices!\nAre you sure?",
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            ev.accept()
            self._app.close()
        else:
            ev.ignore()

