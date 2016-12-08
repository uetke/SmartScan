"""
smo_lantz_drivers.lstepStage

Copyright 2015 Thomas Jollans, Leiden University
"""

import numbers
import time
import warnings

from functools import update_wrapper

import visa

from enum import Enum

from lantz import Q_, Action, Feat, DictFeat
from lantz.messagebased import MessageBasedDriver

class LStepError(EnvironmentError):
    def __init__(self, error_no):
        self._errno = error_no

    def __str__(self):
        return "Error no. {}".format(self._errno)


class LStepStage(MessageBasedDriver):
    """Driver for an OWIS linear stage.
    Does not implement the full LSTEP instruction set.
    """

    DEFAULTS = {
        'COMMON':   {'write_termination': '\r',
                     'read_termination': '\r'},
        'ASRL':     {'baud_rate': 9600,
                     'data_bits': 8,
                     'parity': visa.constants.Parity.none,
                     'stop_bits': visa.constants.StopBits.two,
                     'flow_control': visa.constants.VI_ASRL_FLOW_RTS_CTS}
    }

    _AXIS_INDICES = dict(zip('XYZA', range(4)))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity_factors = None
        self._dims = None
        self._exceptions_enabled = True

    def initialize(self, *a, **kwa):
        super().initialize(*a, **kwa)
        self._number_of_axes = len(self.axes)
        if self.velocity_factors is None:
            self.velocity_factors = [None] * self._number_of_axes
        self.refresh('dimensions')
        self.write('!autostatus 0')

    @property
    def exceptions_enabled(self):
        return self._exceptions_enabled

    @exceptions_enabled.setter
    def exceptions_enabled(self, val):
        # note: this allows 0 and 1, but not other integers.
        if val in (True, False):
            self._exceptions_enabled = val
        else:
            raise TypeError('exceptions_enabled must be a boolean')

    def _raise(self):
        if self._exceptions_enabled:
            error_no = self.error
            if error_no != 0:
                raise LStepError(error_no)

    @Feat()
    def ver(self):
        val = self.query('?ver')
        self._raise()
        return val

    @Feat()
    def sn(self):
        val = self.query('?readsn')
        self._raise()
        return val

    @Feat()
    def status(self):
        val = self.query('?status')
        self._raise()
        return val

    @Feat()
    def error(self):
        return int(self.query('?err'))

    @Feat()
    def axes(self):
        """
        tuple of bools indicating which axes are enabled
        """
        axis_string = self.query('?axis')
        self._raise()
        return tuple(ax == '1' for ax in axis_string.split())

    @axes.setter
    def axes(self, axes):
        axis_string = ' '.join('1' if ax else '0' for ax in axes)
        self.write('!axis ' + axis_string)
        self._raise()

    @property
    def number_of_axes(self):
        return self._number_of_axes

    @DictFeat(keys=('X', 'Y', 'Z', 'A'))
    def axis(self, axis):
        val = '1' == self.query('?axis {}'.format(axis))
        self._raise()
        return val

    @axis.setter
    def axis(self, axis, value):
        self.write('!axis {} {:d}'.format(axis, bool(value)))
        self._raise()

    @Feat()
    def axes_status(self):
        status_string = self.query('?statusaxis')
        self._raise()
        return list(map(AxisStatus, status_string[:self.number_of_axes]))

    @DictFeat(keys='XYZA')
    def axis_status(self, axis):
        return self.axes_status[LStepStage._AXIS_INDICES[axis]]

    @Feat()
    def dimensions(self):
        unit_codes = {
            '0': 'microstep',
            '1': 'µm',
            '2': 'mm',
            '3': 'degree',
            '4': 'revolution'
        }
        self._dims = [unit_codes[dim] for dim in self.query('?dim').split()]
        self._raise()
        return self._dims

    @Feat()
    def positions(self):
        """The current position"""
        val = list(self._parse_position(self.query('?pos')))
        self._raise()
        return val

    @Feat()
    def distances(self):
        """The total distance of the last move"""
        val = list(self._parse_position(self.query('?distance')))        
        self._raise()
        return val

    @DictFeat(keys='XYZA')
    def position(self, axis):
        return self.positions[LStepStage._AXIS_INDICES[axis]]

    @DictFeat(keys='XYZA')
    def distance(self, axis):
        return self.distances[LStepStage._AXIS_INDICES[axis]]

    def _parse_position(self, pos_string):
        if self._dims is None:
            self._dims = self.dimensions
        positions = map(float, pos_string.split())
        for pos, unit in zip(positions, self._dims):
            yield self._in_unit_as_q(pos, unit)

    def _in_unit_as_q(self, n, unit):
        if unit == 'microstep':
            return n
        else:
            return Q_(n, unit)

    @Action()
    def move_absolute(self, axis, destination):
        """
        move the system to a specific position.
        """
        self._move('!moa', axis, destination)

    @Action()
    def move_absolute_multi(self, destination):
        """
        move the system to a specific position.
        """
        self._move('!moa', destination)

    @Action()
    def move_relative(self, axis, distance):
        """
        move the system by a specific distance.
        """
        self._move('!mor', axis, distance)

    @Action()
    def move_relative_multi(self, distances):
        """
        move the system by a specific distance along multiple axes
        """
        self._move('!mor', distances)

    @Action()
    def move_center(self, axis=None):
        """
        center an axis or all axes
        """
        if axis is None:
            self.write('!moc')
        elif axis in list('XYZAxyza'):
            self.write('!moc {}'.format(axis))
        else:
            raise ValueError('Unknows axis {}'.format(axis))
        self._raise()

    @Action()
    def abort(self):
        self.write('!a')
        self._raise()

    def _move(self, command, *args):
        units = self.recall('dimensions')
        if len(args) == 1:
            targets = (self._in_unit_as_number(a, u) for (a,u) in zip(args[0], units))
            command_args = map(str, targets)
        elif len(args) == 2 and args[0] in list('XYZAxyza'):
            axis_idx = LStepStage._AXIS_INDICES[args[0].upper()]
            command_args = [args[0], '{:f}'.format(self._in_unit_as_number(args[1], units[axis_idx]))]
        else:
            raise ValueError('Invalid arguments: {}'.format(args))

        self.write('{} {}'.format(command, ' '.join(command_args)))
        self._raise()

    def _in_unit_as_number(self, value, unit):
        if unit == 'microstep':
            return float(value)
        elif isinstance(value, Q_):
            return value.to(unit).magnitude
        elif isinstance(value, numbers.Real):
            warnings.warn('position or distance supplied without units, assuming correct!')
            return value
        else:
            raise TypeError('do not understand distances of type {}'.format(type(value)))

    @Feat()
    def vel(self):
        """speed in device-specific units (r/s)"""
        val = [float(s) for s in self.query('?vel').split()]
        self._raise()
        return val

    @vel.setter
    def vel(self, velocities):
        self.write('!vel {}'.format(' '.join(map(str, velocities))))
        self._raise()

    @DictFeat(keys='XYZA', units='mm/s')
    def speed(self, axis):
        """The stage speed with units. Requires self.velocity_factors to be set."""
        vel = self.parse_query('?vel {}'.format(axis), format='{:f}')
        val = vel * self.velocity_factors[LStepStage._AXIS_INDICES[axis]]
        self._raise()
        return val

    @speed.setter
    def speed(self, axis, speed):
        vel = speed / self.velocity_factors[LStepStage._AXIS_INDICES[axis]]
        self.write('!vel {} {:.2f}'.format(axis, vel))
        self._raise()

    @Feat()
    def speeds(self):
        return [Q_(vel * fac, 'mm/s') for vel, fac in zip(self.vel, self.velocity_factors)]

    @speeds.setter
    def speeds(self, speeds):
        self.vel = [speed / Q_(fac, 'mm/s') for speed, fac in zip(speeds, self.velocity_factors)]

    def max_speed(self, axis):
        return Q_(15 * self.velocity_factors[LStepStage._AXIS_INDICES[axis]], 'mm/s')
    

    @DictFeat(keys='XYZA', units='m/s^2')
    def acceleration(self, axis):
        val = self.parse_query('?accel {}'.format(axis), format='{:f}')
        self._raise()
        return val

    @acceleration.setter
    def acceleration(self, axis, accel):
        self.write('!accel {} {}'.format(axis, accel))
        self._raise()

    @Feat()
    def calibration_offset_start(self):
        val = list(self._parse_position(self.query('?caliboffset')))
        self._raise()
        return val

    @calibration_offset_start.setter
    def calibration_offset_start(self, offsets):
        self._move('!caliboffset', offsets)

    @Feat()
    def calibration_offset_end(self):
        val = list(self._parse_position(self.query('?rmoffset')))
        self._raise()
        return val

    @calibration_offset_end.setter
    def calibration_offset_end(self, offsets):
        self._move('!rmoffset', offsets)

    @DictFeat(keys='XYZA')
    def limits(self, axis):
        val = tuple(self._parse_position(self.query('?lim {}'.format(axis))))
        self._raise()
        return val

    @limits.setter
    def limits(self, axis, limits):
        self._move('!lim {}'.format(axis), limits)

    @Action()
    def calibrate_start(self, axis=None):
        if axis is None:
            self.write('!cal')
        elif axis in list('XYZAxyza'):
            self.write('!cal {}'.format(axis))
        else:
            raise ValueError('Invalid axis: {}'.format(axis))
        self._raise()

    @Action()
    def calibrate_end(self, axis=None):
        if axis is None:
            self.write('!rm')
        elif axis in list('XYZAxyza'):
            self.write('!rm {}'.format(axis))
        else:
            raise ValueError('Invalid axis: {}'.format(axis))
        self._raise()

    @Feat()
    def trigger_enabled(self):
        val = self.query('?trig') == '1'
        self._raise()
        return val

    @trigger_enabled.setter
    def trigger_enabled(self, trig):
        self.write('!trig {}'.format('1' if trig else '0'))

    @Feat()
    def trigger_axis(self):
        val = self.query('?triga').upper()
        self._raise()
        return val

    @trigger_axis.setter
    def trigger_axis(self, axis):
        if axis in list('XYZAxyza'):
            self.write('!triga {}'.format(axis))
        else:
            raise ValueError('Invalid axis: {}'.format(axis))
        self._raise()

    @Feat()
    def trigger_mode(self):
        val = int(self.query('?trigm'))
        self._raise()
        return val

    @trigger_mode.setter
    def trigger_mode(self, mode):
        self.write('!trigm {}'.format(mode))
        self._raise()

    @Feat(units='µs')
    def trigger_signal_length(self):
        val = self.parse_query('?trigs', format='{:d}')
        self._raise()
        return val

    @trigger_signal_length.setter
    def trigger_signal_length(self, sig):
        if not (0 <= sig <= 5):
            raise ValueError("trigger signal out of range [0; 5]!")
        self.write('!trigs {}'.format(int(sig)))
        self._raise()

    @Feat()
    def trigger_distance(self):
        return self._in_unit_as_q(self.query('?trigd'),
            self.dimensions[LStepStage._AXIS_INDICES[self.trigger_axis.upper()]])

    @trigger_distance.setter
    def trigger_distance(self, distance):
        self.write('!trigd {}'.format(self._in_unit_as_number(distance,
            self.dimensions[LStepStage._AXIS_INDICES[self.trigger_axis.upper()]])))
        self._raise()

    @Feat()
    def trigger_count(self):
        """All performed triggers are counted"""
        val = self.parse_query('?trigcount', format='{:d}')
        self._raise()
        return val

    @trigger_count.setter
    def trigger_count(self, trigs):
        self.write('!trigcount {}'.format(int(trigs)))
        self._raise()

    def wait(self, axis, sleeptime=0.1):
        while self.axis_status[axis] == AxisStatus.moving:
            time.sleep(sleeptime)

    def full_calibration(self, axes=['X'], estimated_stroke_time=15):
        skiptime = estimated_stroke_time * 0.10
        waittime = estimated_stroke_time * 0.80

        for axis in axes:
            self.calibrate_start(axis)
            time.sleep(.2)
            self.wait(axis)
            self.calibrate_end(axis)
            time.sleep(skiptime)
            pos1 = self.position[axis]
            time.sleep(waittime)
            pos2 = self.position[axis]
            speed = (pos2 - pos1) / Q_(waittime, 's')
            mm_per_s = speed.to('mm/s').m
            r_per_s = self.vel[LStepStage._AXIS_INDICES[axis]]
            mm_per_r = mm_per_s / r_per_s
            self.velocity_factors[LStepStage._AXIS_INDICES[axis]] = mm_per_r
            self.wait(axis)

class AxisStatus(Enum):
    ready = '@'
    moving = 'M'
    joystick = 'J'
    in_control = 'C'
    limit_switch = 'S'
    calib_ok = 'A'
    calib_err = 'E'
    stroke_ok = 'D'
    setup = 'U'
    timeout = 'T'
    disabled = '-'

    def is_enabled(self):
        return self != AxisStatus.disabled

    def __repr__(self):
        return '<AxisStatus: {}>'.format(self.human_readable_name())

    def human_readable_name(self):
        return {
            '@': 'Ready',
            'M': 'Moving',
            'J': 'Joystick Mode',
            'C': 'In Control',
            'S': 'Limit Switch Activate',
            'A': 'Calibration OK',
            'E': 'Calibration ERROR',
            'D': 'Table Stroke OK',
            'U': 'Setup',
            'T': 'Timeout',
            '-': 'DISABLED'
        }[self.value]


if __name__ == '__main__':
    import sys
    import concurrent.futures
    with LStepStage('COM2') as owis_stage:
        print('OWIS STAGE')
        print('Firmware version: {}'.format(owis_stage.ver))
        print('S/N: {}'.format(owis_stage.sn))
        print()
        print('Performing calibration procedure')
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            calib_future = executor.submit(owis_stage.full_calibration)
            while calib_future.running():
                sys.stdout.write('\r position: {}               '.format(owis_stage.position['X']))
                sys.stdout.flush()
                time.sleep(0.2)
            exc = calib_future.exception()
            if exc: 
                raise exc
        sys.stdout.write('\r position: {}'.format(owis_stage.position['X']))
        sys.stdout.flush()
        print('\nCalibration:')
        print('Limits: {} {}'.format(*owis_stage.limits['X']))
        print('mm per rev: {:.4f}'.format(owis_stage.velocity_factors[0]))
