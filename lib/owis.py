"""
Module to handle scans involving the OWIS delay line
"""

import logging
import time

from contextlib import contextmanager

from lantz import Q_
from PyQt4.QtCore import QObject, SIGNAL, Qt

from devices import owis_stage

from .app import ScanApplication
from .config import DeviceConfig
from .logger import get_all_caller

class OWISStage(QObject):
    """
    Wrapper around the OWIS stage driver that supports scanning.

    The connection has to be explicitly established (.connect())
    and closed (.close()) due to the nature of serial I/O. For convenience,
    the object is a context manager.
    """
    def __init__(self, device_config=None):
        QObject.__init__(self)

        self.logger = logging.getLogger(get_all_caller())

        if device_config is None:
            device_config = DeviceConfig('IR Delay', 'Serial')

        self._cfg = device_config
        self._stage = owis_stage.LStepStage(device_config['Hardware']['PortID'])
        self._axis = device_config['Hardware']['Axis']
        self._scanning = False

        self._stage.velocity_factors = [device_config['Calibration']['VelocityFactor']] * 4
        self._stage.exceptions_enabled = True

        self._app = ScanApplication()

    def connect(self):
        self.logger.info('Connecting to OWIS stage')
        self._stage.initialize()
        self.logger.info('Connected to OWIS ({} - SN {})'.format(
            self._stage.ver, self._stage.sn))

        self._app.new_logentry.connect(self._on_new_logentry, Qt.DirectConnection, no_receiver_check=True)

    def close(self):
        self._stage.finalize_async()

        self._app.new_logentry.disconnect(self._on_new_logentry)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc_info):
        self.close()

    def check_if_ready(self):
        axis_status = self._stage.axis_status[self._axis]
        self.logger.info('OWIS axis status is {}'.format(axis_status.human_readable_name()))
        return axis_status == owis_stage.AxisStatus.ready

    @property
    def needs_calibration(self):
        ''' This test is probably not reliable! '''
        axis_status = self._stage.axis_status[self._axis]
        return axis_status in (owis_stage.AxisStatus.calib_err,
                               owis_stage.AxisStatus.setup,
                               owis_stage.AxisStatus.disabled)

    def calibrate(self):
        self._stage.full_calibration()

    def _from_mm(self, distance_mm):
        return (self._cfg['Calibration']['Offset'] +
                self._cfg['Calibration']['Slope'] * distance_mm)

    def _to_mm(self, delay):
        return ((delay - self._cfg['Calibration']['Offset'])/
                    self._cfg['Calibration']['Slope'])

    @property
    def is_scanning(self):
        return self._scanning

    def _on_new_logentry(self, entry):
        if not self._scanning:
            entry.add_metadatum('OWIS stage', 'position [ps]', self.get_position())

    @contextmanager
    def _scan(self, start_mm, length_mm, steps, int_time_s, adq,
                    detectors, load_adw_program=True):
        """Do a scan. Blocks!"""
        self._scanning = True

        while not self.check_if_ready():
            self.logger.warn('waiting for stage!')
            time.sleep(1)

        stage = self._stage

        # We want to revert to the old speed of the stage later
        old_speed = stage.speed[self._axis]

        stage.trigger_enabled = False
        stage.vel = [10, 10]
        # Send the stage to its start position
        stage.move_absolute_async(self._axis, Q_(start_mm, 'mm'))
        self.logger.info('moving OWIS stage to start position')

        length = Q_(length_mm, 'mm')
        trig_dist = length / steps
        total_time = steps * Q_(int_time_s, 's')
        speed = length / total_time

        if speed >= stage.max_speed(self._axis):
            raise ValueError('Scan too fast! Max stage speed is {}, calculated speed {}'
                .format(stage.max_speed(self._axis), speed))

        try:

            # configure the trigger (while the stage is moving)
            stage.trigger_axis = self._axis
            stage.trigger_mode = 1
            stage.trigger_signal_length = Q_(5, 'µs')
            stage.trigger_distance = trig_dist

            # wait for the stage to come to rest
            while not self.check_if_ready():
                time.sleep(0.5)

            adwin_scan = adq.scan_external(detectors, steps, load_program=load_adw_program)

            stage.speed[self._axis] = speed
            stage.trigger_enabled = True

            # overshoot by one step. This is not strictly necessary,  but it *may* be 
            # required to compensate for rounding errors...
            # wait for the stage to come to rest
            while not self.check_if_ready():
                time.sleep(0.5)
            stage.move_relative('X', length * (1 + 1/steps))
            time.sleep(0.3)

            if self.check_if_ready():
                print('axis status ready?!, device status', stage.status)

            yield adwin_scan

            adwin_scan.wait()

        finally:

            time.sleep(0.5)

            stage.trigger_enabled = False
            self._stage.speed['X'] = Q_(10, 'mm/s')
            #stage.vel = [10, 10]
            # Send the stage to its start position
            stage.move_absolute_async(self._axis, Q_(start_mm, 'mm'))
            #stage.speed[self._axis] = old_speed
            self._scanning = False

    def goto(self, position):
        #self._stage.vel = [10, 10]
        self._stage.speed['X'] = Q_(10, 'mm/s')
        dest = Q_(self._to_mm(position), 'mm')
        if not (Q_(0, 'mm') <= dest <= Q_(155, 'mm')):
            raise ValueError('Destination {} out of range'.format(dest))
        return self._stage.move_absolute_async(self._axis, dest)

    def scan(self, start, length, steps, delta_t, adq, detectors, *, load_adw_program=True):
        """
        Do a scan in coöperation with the ADwin box.

        Parameters:
        start - start position (in units of the calibration)
        length - length of the scan (ditto)
        steps - number of pixels to acquire
        delta_t - (integration) time between datapoint acquisition
        load_adw_program - do we need to load the "external scan" program into the ADwin box?

        This method returns a context manager that yields an instance of adq_mod.ScanFuture.
        If exited before the scan is done, the context manager blocks. It *should* be exited 
        before starting a new scan or moving the stage (but this is not crucial). It MUST NOT
        be exited while another scan is running.
        """
        return self._scan(self._to_mm(start), self._to_mm(length), steps,
                          delta_t, adq, detectors, load_adw_program=load_adw_program)

    def get_position(self):
        return self._from_mm(self._stage.position[self._axis].to('mm').m)



