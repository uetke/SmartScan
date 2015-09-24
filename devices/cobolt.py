# -*- coding: utf-8 -*-
"""
    lantz.drivers.cobolt.rumba
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the drivers to control an Optical Power Meter.

    :copyright: 2012 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.

    Source: Instruction Manual (Cobolt)
"""


from pyvisa import constants

from lantz.feat import Feat
from lantz.action import Action
from lantz.messagebased import MessageBasedDriver


class rumba(MessageBasedDriver):
    """ Cobolt Rumba Driver.
        Also works with Zouk, Calypso, Samba, Jive, Flamenco.
    """

    DEFAULTS = {'ASRL': {'write_termination': '\r',
                         'read_termination': '\r',
                         'baud_rate': 115200,
                         'data_bits': 8,
                         'parity': constants.Parity.none,
                         'stop_bits': constants.StopBits.one,
                         'encoding': 'ascii',
                         'timeout': 2000
                        }}

    @Feat
    def idn(self):
        """ Gets the serial number.
        """
        return self.query('sn?')

    @Feat
    def hours(self):
        """ Retrieves the value from the Laser.
        """
        return float(self.query('hrs?'))

    @Feat(values={'Open': 1, 'OK': 0})
    def interlock(self):
        """ Retrieves the status of the interlock.
        """
        return int(self.query('ilk?'))

    @Feat(values={'OFF': 0, 'ON': 1})
    def laser(self):
        """ Get laser ON/OFF state.
        """
        return int(self.query('l?'))

    @Feat
    def output_power(self):
        """ Get set output power. In Watts.
        """
        return float(self.query('p?'))

    @output_power.setter
    def output_power(self, value):
        """ Set the output power. In Watts.
        """
        self.write('p {}'.format(value))

    @Feat
    def read_power(self):
        """ Read the output power.
        """
        return float(self.query('pa?'))

    @Feat
    def get_drive_current(self):
        """ Get drive current. In Amps
        """
        return float(self.query('i?'))
