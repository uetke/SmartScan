# -*- coding: utf-8 -*-
"""
    lantz.drivers.stanford.sr844
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2012 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import numpy as np

from lantz import Action, Feat, DictFeat, ureg, Q_
from lantz.drivers.legacy.serial import SerialDriver
from lantz.errors import InstrumentError

from collections import OrderedDict
import numpy as np
import logging
from logger import get_all_caller

display_output = OrderedDict([('X', '0'),
                              ('Y', '0'),
                              ('X/Y', '0'),
                              ('Rv', '1'),
                              ('Theta', '1'),
                              ('RdB', '2'),
                              ('YnoiseV', '2'),
                              ('Xnoise', '3'),
                              ('YnoisedB', '3'),
                              ('AUX', '4')])

    
class _SR844(object):
    def __init__(self,port):
        super().__init__(port)
        super().initialize() # Automatically open the port
        self.TIMEOUT = 20
        self.sens = np.array([1e-7,3e-7,1e-6,3e-6,1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1]) #Units in Volt
        self.timecnst = np.array([1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1e-0,3e-0,1,3,1e2,3e2,1,1e3,3e3]) #Units in seconds
        self.timecnstfilt = np.array([0,6,8,12,18,24]) #Units in dB/oct
        self.sample_rates = np.array([62.5e-3,125e-3,250e-3,500e-3,1,2,4,8,16,32,64,128,256,512,0]) #Units in Hz
    
    @Feat()
    def idn(self):
        return self.query  ('*IDN?')  
    
    @Feat(units='degrees', limits=(-360, 360, 0.01))
    def reference_phase_shift(self):
        """Phase shift of the reference.
        """
        return self.query('PHAS?')

    @reference_phase_shift.setter
    def reference_phase_shift(self, value):
        self.send('PHAS{:.2f}'.format(value))

    @Feat(values={True: '1', False: '0'})
    def reference_internal(self):
        """Reference source.
        """
        return self.query('FMOD?')

    @reference_internal.setter
    def reference_internal(self, value):
        self.send('FMOD {}'.format(value))

    @Feat(units='Hz', limits=(5e4, 2e8))
    def frequency(self):
        """Reference frequency.
        """
        return self.query('FREQ?')

    @frequency.setter
    def frequency(self, value):
        self.send('FREQ{:.5f}'.format(value))

    @Feat(values={True: '0', False: '1'})
    def harmonic(self):
        """Detection harmonic.
        (detect at F, i=0) or ON, (detect at 2F, i=1).
        """
        return self.query('HARM?')

    @harmonic.setter
    def harmonic(self, value):
        self.send('HARM {}'.format(value))

    # Signal input
    @Feat(values={'High': '0', 'Normal': '1', 'Low': '2'})
    def wide_reserve_mode(self):
        return self.query('WRSV ?')
    
    @wide_reserve_mode.setter
    def wide_reserve_mode(self,value):
        self.send('WRSV {}'.format(value))
        
    # GAIN and TIME CONSTANT COMMANDS.

    @Feat(values={False: '0', True: '1'})
    def rel_mode(self):
        """REL mode.
        """
        return self.query('RMOD?')

    @rel_mode.setter
    def rel_mode(self, value):
        self.send('RMOD {}'.format(value))

    @Feat(units='dB')
    def filter_db_per_oct(self):
        """Time constant.
        """
        return self.timecnstfilt[int(self.query('OFSL?'))]

    @filter_db_per_oct.setter
    def filter_db_per_oct(self, value):
        #if value=0 then no filter is set
        option = np.abs(self.timecnstfilt-value).argmin()
        if (self.timecnstfilt==value).any():
            print('Value %s is not a option pick nearest' %value)
            print('Nearest value is %s' %self.sens[option])
            #self.logger.warning('Value %s is not a option pick nearest' %value)
            #self.logger.warning('Nearest value is %s' %self.sens[option])
        self.send('OFSL %s' %option)
        
    @Feat(units='V')
    def sensitivity(self):
        return self.sens[int(self.query('SENS ?'))]
        
    @sensitivity.setter
    def sensitivity(self,value):
        print(value)
        option = np.abs(self.sens-value).argmin()
        if not (self.sens==value).any():
            print('Value %s is not a option pick nearest' %value)
            print('Nearest value is %s' %self.sens[option])
            #self.logger.warning('Value %s is not a option pick nearest' %value)
            #self.logger.warning('Nearest value is %s' %self.sens[option])
        self.send('SENS %s' %option)
        
    @Feat(units='s')
    def timeconstant(self):
        return self.timecnst[int(self.query('OFLT ?'))]
        
    @timeconstant.setter
    def timeconstant(self,value):
        option = np.abs(self.timecnst-value).argmin()
        if not (self.timecnst==value).any():
            print('Value %s is not a option pick nearest' %value)
            print('Nearest value is %s' %self.timecnst[option])
            #self.logger.warning('Value %s is not a option pick nearest' %value)
            #self.logger.warning('Nearest value is %s' %self.sens[option])
        self.send('OFLT %s' %option)

    @Feat(values={'High': 0, 'Normal': 1, 'Low':2})
    def close_reserve_mode(self):
        return self.query('CRSV ?')
    
    @wide_reserve_mode.setter
    def close_reserve_mode(self,value):
        self.send('CRSV {}'.format(value))
        
    ## DISPLAY and OUTPUT COMMANDS

    @DictFeat(keys={1, 2}, values=display_output)
    def display(self, channel):
        """Front panel output source.
        """
        return self.query('DDEF? {}'.format(channel))

    @display.setter
    def display(self, channel, value):
        self.send('DDEF {}, {}'.format(channel, value))

    @DictFeat(keys={1, 2}, values={'Display': 0, 'X': 1, 'Y': 1})
    def front_output(self, channel):
        """Front panel output source.
        """
        return int(self.query('FPOP? {}'.format(channel)))

    @front_output.setter
    def front_output(self, channel, value):
        self.send('FPOP {}, {}'.format(channel, value))

    # OEXP

    # AOFF is below.

    ## AUX INPUT and OUTPUT COMMANDS

    @DictFeat(keys={1, 2}, units='volt')
    def analog_input(self, key):
        """Input voltage in the auxiliary analog input.
        """
        self.query('AOUX? {}'.format(key))

    @DictFeat(None, keys={1, 2}, units='volt', limits=(-10.5, 10.5))
    def analog_output(self, key):
        """Ouput voltage in the auxiliary analog output.
        """
        self.query('AUXV? {}'.format(key))

    @analog_output.setter
    def analog_output(self, key, value):
        self.query('AUXV {}, {}'.format(key, value))


    ## SETUP COMMANDS

    remote = Feat(None, values={True: 0, False: 1})

    @remote.setter
    def remote(self, value):
        """Lock Front panel.
        """
        self.query('OVRM {}'.format(value))

    @Feat(values={True: '1', False: '0'})
    def key_click_enabled(self):
        """Key click
        """
        return self.query('KCLK?')

    @key_click_enabled.setter
    def key_click_enabled(self, value):
        return self.send('KCLK {}'.format(value))

    @Feat(values={True: '1', False: '0'})
    def alarm_enabled(self):
        """Key click
        """
        return self.query('ALRM?')

    @alarm_enabled.setter
    def alarm_enabled(self, value):
        return self.send('ALRM {}'.format(value))

    @Action(limits=(1, 9))
    def recall_state(self, location):
        """Recalls instrument state in specified non-volatile location.

        :param location: non-volatile storage location.
        """
        self.send('RSET {}'.format(location))

    @Action(limits=(1, 9))
    def save_state(self, location):
        """Saves instrument state in specified non-volatile location.

        Previously stored state in location is overwritten (no error is generated).
        :param location: non-volatile storage location.
        """
        self.send('SSET {}'.format(location))


    ## AUTO FUNCTIONS

    def wait_bit1(self):
        pass

    @Action()
    def auto_gain_async(self):
        """Equivalent to press the Auto Gain key in the front panel.
        Might take some time if the time constant is long.
        Does nothing if the constant is greater than 1 second.
        """
        self.send('AGAN')

    @Action()
    def auto_gain(self):
        self.auto_gain_async()
        self.wait_bit1()

    @Action()
    def auto_reserve_async(self):
        """Equivalent to press the Auto Reserve key in the front panel.
        Might take some time if the time constant is long.
        """
        self.send('ARSV')

    @Action()
    def auto_reserve(self):
        self.auto_reserve_async()
        self.wait_bit1()

    @Action()
    def auto_phase_async(self):
        """Equivalent to press the Auto Phase key in the front panel.
        Might take some time if the time constant is long.
        Does nothing if the phase is unstable.
        """
        self.send('APHS')

    @Action()
    def auto_phase(self):
        self.auto_phase_async()
        self.wait_bit1()

    @DictFeat(keys={1, 2}, values={'X': 0, 'Rv':1,'RdB':2,'y': 0})
    def auto_offset_async(self, channel_name):
        """Automatically offset a given channel to zero.
        Is equivalent to press the Auto Offset Key in the front panel.

        :param channel_name: the name of the channel.
        """
        self.send('AOFF {}'.format(channel_name))

    @Action()
    def auto_offset(self):
        self.auto_offset_async()
        self.wait_bit1()


    ## DATA STORAGE COMMANDS

    @Feat(units = 'Hz')
    def sample_rate(self):
        """Sample rate.
        """
        return self.query('SRAT?')

    @sample_rate.setter
    def sample_rate(self, value):
        self.send('SRAT {}'.format(value))

    @Feat(values={True: '0', False: '1'})
    def single_shot(self):
        """End of buffer mode.

        If loop mode (single_shot = False), make sure to pause data storage
        before reading the data to avoid confusion about which point is the
        most recent.
        """
        return self.query('SEND?')

    @single_shot.setter
    def single_shot(self, value):
        self.send('SEND {}'.format(value))

    @Action()
    def trigger(self):
        """Software trigger.
        """
        self.send('TRIG')

    @Feat(values={True: '0', False: '1'})
    def trigger_start_mode(self):
        """The TSTR command sets or queries the Trigger Scan Mode to On (1) or Off (0).
        When Trigger Scan Mode is On (i=1), an external or software trigger starts the
        scan. This mode is only applicable for fixed data sample rates set by SRAT
        0-13."""
        self.query('TSTR?')

    @trigger_start_mode.setter
    def trigger_start_mode(self, value):
        self.send('TSTR {}'.format(value))

    @Action()
    def start_data_storage(self):
        """Start or resume data storage
        """
        self.send('STRT')

    @Action()
    def pause_data_storage(self):
        """Pause data storage
        """
        self.send('PAUS')

    @Action()
    def reset_data_storage(self):
        """Reset data buffers. The command can be sent at any time -
        any storage in progress, paused or not. will be reset. The command
        will erase the data buffer.
        """
        self.send('REST')


    ## DATA TRANSFER COMMANDS

    @DictFeat(keys={'X', 'Y', 'Rv', 'RdB', 'Theta', 1, 2})
    def analog_value(self, key):
        i = {'X': '1', 'Y': '2', 'Rv': '3', 'RdB': '4', 'Theta': '5'}
        if key in i.keys():
            return self.query('OUTP? {}'.format(i[key]))
        else:
            return self.query('OUTR? {}'.format(key))

    @Action()
    def measure(self, channels):
        """ The SNAP? command returns the values of up to six parameters at a single
        instant. The SNAP? command requires at least two and at most six parameters
        """
        if 2<=len(channels)<=6:
            d = {'X': '1', 'Y': '2', 'Rv': '3', 'RdB': '4','Theta': '5',
                'AUX1': '6', 'AUX2': '7', 'RefFreq': '8', 'Ch1': '9',
                'Ch2': '10'}
            channels = ','.join(d[ch] for ch in channels)
            return self.query('SNAP? {}'.format(channels))
        else:
            self.logger.error('Length {} is out of range(2,7)'.format(len(channels)))

    # OAUX See above

    @Feat()
    def buffer_length(self):
        return self.query('SPTS?')

    @Action()
    def read_buffer(self, channel, start=0, length=None, format='A'):
        """Queries points stored in the Channel buffer

        :param channel: Number of the channel (1, 2).
        :param start: Index of the buffer to start.
        :param length: Number of points to read.
                       Defaults to the number of points in the buffer.
        :param format: Transfer format
                      'a': ASCII (slow)
                      'b': IEEE Binary (fast) - NOT IMPLEMENTED
                      'c': Non-IEEE Binary (fastest) - NOT IMPLEMENTED
        """

        cmd = 'TRCA'
        if not length:
            length = self.buffer_length
        self.send('{}? {},{},{}'.format(cmd, channel, start, length))
        if cmd == 'TRCA':
            data = self.recv()
            return np.fromstring(data, sep=',') * ureg.volt
        else:
            raise ValueError('{} transfer format is not implemented'.format(format))

    # Fast
    # STRD

class SR844GPIB(_SR844, ):

    RECV_TERMINATION = '\r'
    SEND_TERMINATION = '\n'

class SR844Serial(_SR844, SerialDriver):

    RECV_TERMINATION = '\r'
    SEND_TERMINATION = '\n'



if __name__ == '__main__':
    SR844 = SR844Serial('COM10')
    print(SR844.idn)
    from xml2dict import device
    lockin = device('Serial','Lock-in')
    for key,value in eval(lockin.properties['Output']['Calibration']['Init']).items():
        try:
            print('SR844.%s = value' %key)
            exec('SR844.%s = value' %key)
        except ValueError:
            print('SR844.%s = Q_(value)' %key)
            exec('SR844.%s = Q_(value)' %key)
    
    
    

    