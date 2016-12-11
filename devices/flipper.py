""" For this class to work, it is important to have the 'Thorlabs.MotionControl.FilterFlipper.dll'
file in the system path. It comes with the kinesis software provided by Thorlabs. It can be downloaded from there
https://www.thorlabs.de/Software/Motion%20Control%5CKINESIS%5CApplication%5CKINESIS%20Install%20x64%5Csetup.exe
And the default installation path should be added to the system path.
C:\Program Files\Thorlabs\Kinesis
Only copying the dll doesn't satisfy all the dependences. Apparently a full installation is needed, but didn't go
into the details."""

from ctypes import c_long, c_buffer, c_float, windll, pointer
import os



class Flipper():
    def __init__(self, SerialNum):
        self.Connected = False
        self.SerialNum = SerialNum
        dllname = 'Thorlabs.MotionControl.FilterFlipper.dll'
        self.aptdll = windll.LoadLibrary('Thorlabs.MotionControl.FilterFlipper.dll')
        
        # This is called by the user!
        #self.initializeHardwareDevice()


    def initializeHardwareDevice(self):
        '''
        Initialises the motor.
        You can only get the position of the motor and move the motor after it has been initialised.
        Once initiallised, it will not respond to other objects trying to control it, until released.
        '''
        try:
            result = self.aptdll.FF_Open(self.SerialNum)
        except:
            raise IOError('Could not open the device identified as %s'.format(self.SerialNum))

        if result == 0:
            self.aptdll.FF_RequestStatus(self.SerialNum)
            self.aptdll.FF_StartPolling(self.SerialNum,c_long(200))
            self.connected = True
        else:
            self.connected = False
            raise IOError('Could not open the device identified as %s'.format(self.SerialNum))

    def identify(self):
        '''
        Causes the motor to blink the Active LED
        '''
        self.aptdll.FF_Identify(self.SerialNum)
        return True

    def close(self):
        '''
        Releases the APT object
        Use when exiting the program
        '''
        self.aptdll.FF_StopPolling(self.SerialNum)
        self.aptdll.FF_ClearMessageQueue(self.SerialNum)
        self.aptdll.FF_Close(self.SerialNum)
        self.Connected = False


    def getPos(self):
        ''' Obtain the current position of the filter.
            ..:Can be 1 or 2.
        '''
        if not self.connected:
            raise Exception('Please connect first! Use initializeHardwareDevice')

        position = self.aptdll.FF_GetPosition(self.SerialNum)
        if position not in (1,2):
            pass#raise Warning('The flipper returned an invalid position: %s'%(position))
        return position

    def goto(self,position):
        """ Goes to the specified position.
            ..: It can be either 1 or 2.
        """
        if not self.connected:
            raise Exception('Please connect first! Use initializeHardwareDevice')

        if position not in (1,2):
            raise Exception('Position can only be 1 or 2')
        self.aptdll.FF_MoveToPosition(self.SerialNum,c_long(position))
        return self.getPos()

    def changePos(self):
        """ Changes the position of the filter.
        """
        if not self.connected:
            raise Exception('Please connect first! Use initializeHardwareDevice')
        if self.getPos() == 1:
            n = 2
        else:
            n = 1
        self.goto(n)


if __name__ == '__main__':
    from time import sleep

    #inst1 = Flipper(SerialNum=b'37864186')
    inst2 = Flipper(SerialNum=b'37863355')
    #print(inst1.identify()) # Makes the green LED blink
    print(inst2.identify()) # Makes the green LED blink
    sleep(1)
    #print('Current position of flipper 1 is %s'%(inst1.getPos()))
    print('Current position of flipper 2 is %s'%(inst2.getPos()))
    change_pos = True
    while change_pos:
        p = int(input('Change the position [11,12,21,22,0=exit]'))
        if p==11:
            print('Changing position...')
            #inst1.goto(1)
        elif p==12:
            print('Changing position...')
            #inst1.goto(2)
        elif p==21:
            print('Changing position...')
            inst2.goto(1)
        elif p==22:
            print('Changing position...')
            inst2.goto(2)
        else:
            change_pos = False
    print('The fianl position is %s'%inst2.getPos())
    inst2.close()
