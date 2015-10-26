# -*- coding: utf-8 -*-
"""
    lantz.drivers.acton.a500i
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements the drivers to control a Monochromator based on the Acton 500-i.
    :copyright: 2015 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.

    Source: Instruction Manual (Newport)
"""

from pyvisa import constants

from lantz.feat import Feat
from lantz.action import Action
from lantz.messagebased import MessageBasedDriver


class a500i(MessageBasedDriver):
    """ Acton 500-i monochromator. It is also used as spectrometer
    """

    DEFAULTS = {'ASRL': {'write_termination': '\r',
                         'read_termination': '\r',
                         'baud_rate': 9600,
                         'data_bits': 8,
                         'parity': constants.Parity.none,
                         'stop_bits': constants.StopBits.one,
                         'encoding': 'ascii',
                         'timeout': 2000
                        }}

    @Feat(limits=(0,2000,.001))
    def goto(self,wl):
        """ Goes to the desired wavelength value. At maximum motor speed
        """
        return self.write('%s GOTO'%(wl))

    @Feat(limits=(0,2000,.001))
    def nm(self):
        """ Gets the current central wavelength.
        """
        ans = self.query('?NM')
        ans.split(' ')
        return float(ans[1])

    @nm.setter
    def nm(self,wl):
        """ Goes to the desired wavelength value with the latest motor speed set.
        """
        return self.write('%s NM'%wl)

    def getgrating(self):
        """ Returns the number of gratings presently being used numbered 1-9.
        """
        return self.query('?GRATING')

    def getgratings(self):
        """ Returns the list of installed gratings with postiion groove density and blaze.
            The present grating is specified with an arrow
        """
        return self.query('?GRATINGS')

    def side(self):
        """ Moves the designated diverter mirror to postiion the beam to the side port postiion.
        """
        self.write('SIDE')
        return True

    def front(self):
        """ Moves the designated diverter mirror to position the beam to the front port position.
        """

    def getmirror(self):
        """ Returns the position of the designated mirror with the responses 'front' and 'side'
        """
        return self.query('?MIRROR')

    def idn(self):
        """ Identifies the device by returning its serial number.
        """
        return self.query('SERIAL')

    def model(self):
        """ Returns the model of the spectrometer.
        """
        self.query('MODEL')

if __name__ == '__main__':
    import argparse
    import lantz.log

    parser = argparse.ArgumentParser(description='Test Kentech HRI')
    parser.add_argument('-p', '--port', type=str, default='1',
                        help='Serial port to connect to')

    args = parser.parse_args()
    lantz.log.log_to_socket(lantz.log.DEBUG)

    with a500i.via_serial(args.port) as inst:

        # inst.lockout = True # Blocks the front panel
        # inst.keypad = 'Off' # Switches the keypad off
        # inst.attenuator = True # The attenuator is on
        # inst.wavelength = 633 # Sets the wavelength to 633nm
        # inst.units = "Watts" # Sets the units to Watts
        # inst.filter = 'Slow' # Averages 16 measurements
        #
        # if not inst.go:
        #     inst.go = True # If the instrument is not running, enables it
        #
        # inst.range = 0 # Auto-sets the range

        print('The model is {}'.format(inst.idn()))
        print('The central wavelength is %s'%(inst.nm()))
        inst.goto(532.1)
        print('The central wavelength is %s'%(inst.nm()))