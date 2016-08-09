"""
Module to handle scans involving the OWIS delay line
"""

import logging
import time

from contextlib import contextmanager

from lantz import Q_

from devices import owis_stage

from .config import DeviceConfig
from .logger import get_all_caller

class OWISStage:
    """
    Wrapper around the OWIS stage driver that supports scanning.

    The connection has to be explicitly established (.connect())
    and closed (.close()) due to the nature of serial I/O. For convenience,
    the object is a context manager.
    """
    def __init__(self, device_config=None):
        self.logger = logging.getLogger(get_all_caller())

        if device_config is None:
            device_config = DeviceConfig('IR Delay', 'Serial')

        self._stage = owis_stage.LStepStage(device_config['Hardware']['PortID'])
        self._axis = device_config['Hardware']['Axis']

        self._stage.velocity_factors = [device_config['Calibration']['VelocityFactor']] * 4

    def connect(self):
        self.logger.info('Connecting to OWIS stage')
        self._stage.initialize()
        self.logger.info('Connected to OWIS ({} - SN {})'.format(
            self._stage.ver, self._stage.sn))

    def close(self):
        self._stage.finalize()

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

    @contextmanager
    def _scan(self, start_mm,length_mm, steps, int_time_s, adq,
                    detectors, load_adw_program=True):
        """Do a scan. Blocks!"""
        stage = self._stage

        # We want to revert to the old speed of the stage later
        old_speed = stage.speed[self._axis]

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
            while stage.axis_status[self._axis] == owis_stage.AxisStatus.moving:
                time.sleep(0.2)

            adwin_scan = adq.scan_external(detectors, steps, load_program=load_adw_program)

            stage.speed[self._axis] = speed
            stage.trigger_enabled = True
            stage.move_relative_async('X', length)

            yield adwin_scan

            adwin_scan.wait()

        finally:

            stage.trigger_enabled = False
            stage.speed[self._axis] = old_speed



