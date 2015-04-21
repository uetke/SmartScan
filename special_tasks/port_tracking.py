# Simple port tracking for python

from lib.adq_mod import *
from time import sleep
if __name__ == '__main__':
    adw = adq('lib/adbasic/adwin.T99') 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    
    while True:
        status = adw.get_data(data.properties['output_status'],8)
        status = status[:]
        
        x_port = int(xpiezo.properties['Output']['Hardware']['PortID'])
        calibration=xpiezo.properties['Output']['Calibration'] 
        x_pos = calibration['Slope']*status[x_port-1]+calibration['Offset']
        
        y_port = int(ypiezo.properties['Output']['Hardware']['PortID'])
        calibration=ypiezo.properties['Output']['Calibration'] 
        y_pos = calibration['Slope']*status[y_port-1]+calibration['Offset']
        
        z_port = int(zpiezo.properties['Output']['Hardware']['PortID'])
        calibration=zpiezo.properties['Output']['Calibration'] 
        z_pos = calibration['Slope']*status[z_port-1]+calibration['Offset']
        
        print([x_pos,y_pos,z_pos])
        sleep(.5)