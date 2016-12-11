'''
The flask-based web app for controlling shutters
'''

import os.path
from collections import deque
import time

from PyQt4 import QtCore

from scantools import ScanApplication
from scantools.devices.shutters import Shutter, ThorlabsFlipper, ShutterConflict

from flask import Blueprint, render_template, request, jsonify

webapp_root_dir = os.path.dirname(__file__)

shutters_webapp = Blueprint('shutters', __name__,
                            template_folder=os.path.join(webapp_root_dir, 'templates'),
                            static_folder=os.path.join(webapp_root_dir, 'static'))

@shutters_webapp.route('/')
def index():
    scan_app = ScanApplication()
    shutter_service = scan_app.get_service("ShutterService")

    return render_template("shutters.html", shutters=shutter_service.shutters,
                                            flippers=shutter_service.flippers,
                                            timestamp=time.time())


_event_tracker = None

@shutters_webapp.route('/get-events')
def get_events():
    global _event_tracker
    if _event_tracker is None:
        _event_tracker = EventTracker()

    timestamp = float(request.args['timestamp'])
    events = _event_tracker.get_since(timestamp)
    return jsonify(timestamp=time.time(),
                   events=events)

@shutters_webapp.route('/set-state', methods=['POST'])
def set_state():
    scan_app = ScanApplication()
    shutter_service = scan_app.get_service("ShutterService")

    device_type = request.form['type']
    name = request.form['name']
    new_state = int(request.form['state'])

    if device_type == 'shutter':
        device = shutter_service.get_shutter(name)
    elif device_type == 'flipper':
        device = shutter_service.get_flipper(name)
    else:
        return jsonify(error='bad request'), 400

    try:
        device.state = new_state
        return jsonify(status='ok')
    except ShutterConflict.Violation as err:
        return jsonify(status='error', error='Conflict with {}'.format(str(err)))


class EventTracker(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self._app = ScanApplication()
        self._shutter_service = self._app.get_service("ShutterService")

        self.events = deque()

        self._shutter_service.any_state_changed.connect(self.on_any_state_changed,
                                                        QtCore.Qt.DirectConnection)

    def on_any_state_changed(self, device):
        t = time.time()

        if isinstance(device, Shutter):
            type_name = 'shutter'
        elif isinstance(device, ThorlabsFlipper):
            type_name = 'flipper'
        else:
            return
        if device.state is None:
            # no need to communicate null states of flippers...
            return

        ev = {
            'type': type_name,
            'name': device.name,
            'state': int(device.state)
        }
        self.events.append((t, ev))

        while len(self.events) > 20:
            self.events.popleft()

    def get_since(self, timestamp, *, block=True):
        events = []
        for (t, ev) in self.events:
            if t > timestamp:
                events.append(ev)

        if block:
            while not events:
                time.sleep(0.05)
                events = self.get_since(timestamp, block=False)
        return events
        

