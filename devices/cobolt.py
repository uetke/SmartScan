# -*- coding: utf-8 -*-
"""
    lantz.drivers.cobolt.rumba
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the drivers to control an Optical Power Meter.

    :copyright: 2012 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
    
    Source: Instruction Manual (Newport)
"""

from lantz.feat import Feat
from lantz.action import Action
from lantz.serial import SerialDriver
from lantz.errors import InvalidCommand


class rumba(SerialDriver):
    """ Newport 1830c Power Meter
    """
    
    ENCODING = 'ascii'
    RECV_TERMINATION = '\r'
    SEND_TERMINATION = '\r'
    TIMEOUT = 1
    
    def __init__(self, port=7,baudrate=115200):
        super().__init__(port, baudrate)#, bytesize=8, parity='None', stopbits=1) 
    
    def initialize(self):
        super().initialize() 
        
    def hours(self):
        """ Retrieves the value from the Laser.
        """        
        return float(self.query('hrs?'))