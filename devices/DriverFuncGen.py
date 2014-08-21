from __future__ import division 
from lantz.usb import USBDriver
from lantz.drivers.usbtmc import USBTMCDriver
from lantz.action import Action
from lantz import DictFeat
from lantz import Feat, Q_
import numpy as np


class funcgen(USBDriver):
    """The agilent 33220a function generator"""

    
    freqlimits = {'SIN':(1e-6,20e6),'SQUare':(1e-6,20e6),'RAMP':(1e-6,200e3),'PULS':(500e-6,5e6)}
    def __init__(self, port):
        """initialization of the class"""
        super().__init__(port)
        super().initialize() # Automatically open the port
        print(self.idn())
        self.TIMEOUT = 20
        V = Q_(1, 'V')
        Hz = Q_(1, 'Hz')
        self.func = 'SIN'  #Options are SIN,SQUare,RAMP,PULS,DC
        self.freq = 550e3 * Hz
        self.ampl = 5 * V #Amplitude peak2peak in volt min=10mVpp, max=10Vpp
        self.offset = 2.5 * V #Offset of the signal |offset| <= 10 - Vpp/2
        self.apply(self.func, self.freq, self.ampl, self.offset)
        
    def idn(self):
        return self.send(bytes('*IDN?\n','ascii'))
    
    def apply(self,func=None,freq=None,ampl=None,offset=None):
        if not func==None: 
            self.set_function_type(func)
        if not freq==None: 
            self.set_frequency(freq)
        if not ampl==None: 
            self.set_amplitude(ampl)
        if not offset==None: 
            self.set_offset(offset)

    #@DictFeat(keys=['SIN','SQUare','RAMP','PULS','DC'])
    def set_function_type(self,func):
        self.send('FUNC %s' %func)
    
    #@Feat(units='Hz', limits=freqlimits[self.func])
    def set_frequency(self,freq):
        self.send('FREQ %s' %freq)
    
    #@Feat(units='V', limits=(10e-3,10))
    def set_amplitude(self,ampl):
        self.send('VOLT %s' %ampl)
    
    #@Feat(units='V', limits=(-10+self.ampl/2,10-self.ampl/2))    
    def set_offset(self, offset):
        self.send('VOLT:OFFS %s' %offset)
            
    def get_wfrm_setting(self):
        """returns the waveform settings
           example format 'func type freq,amplitude,offset'
           'SIN +5.0000000000000E+03,+3.0000000000000E+00,-2.5000000000000E+00' """
        return self.query('APPL?')
    
if __name__ == '__main__':
    funcgen2 = funcgen(0x0957)

        