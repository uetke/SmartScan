# Script for acquiring timetraces vs intensity of the selected particle

from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
import msvcrt
import sys
import os
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import PowerMeter1830c as pp
from winsound import Beep

logger=logger(filelevel=20)


def abort(filename):
    logger = logging.getLogger(get_all_caller())
    logger.critical('You quit!')
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_abort.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Aborted file saved as %s%s_abort.txt' %(savedir,filename))
    sys.exit(0)

if __name__ == '__main__':
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    # Check if the calibration of the AOM was done today and import the data for it.
    if os.path.exists(savedir+'aom_calibration.txt'):
        print('Importing AOM calibration...')
        AOM_voltage = np.loadtxt(savedir+'aom_calibration2.txt').astype('float')[6:]
        intensity = np.loadtxt(savedir+'aom_calibration.txt').astype('float')[6:]
        P = np.polyfit(intensity,AOM_voltage,2)
        print(P)
        #plt.plot(intensity,AOM_voltage,'.')
        #plt.plot(intensity,np.polyval(P,intensity))
        #plt.ylabel('AOM voltage (V)')
        #plt.xlabel('Laser intensity (uW)')
        #plt.show()
    else:
        raise Exception('The AOM was not calibrated today, please do it before running this program...')

    number_of_times = 11
    laser_min = 10 # In uW
    laser_max = 150 # In uW
    timetrace_time = 5 # In seconds
    integration_time = .0001 # In seconds
    
    
    laser_powers = np.linspace(laser_min,laser_max,number_of_times)
    print('633 laser powers to be used:')
    print(laser_powers)
    #initialize the adwin and the devices
    name = 'power_intensity_trap'

    i=1
    filename = '%s_%s.dat.npy'%(name,i)
    while os.path.exists(savedir+filename):
        i += 1
        filename = '%s_%s.dat.npy' %(name,i)

    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s'%(savedir+filename))
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq()
    counter = device('APD 1')
    counter2 = device('APD 2')
    qpdx = device('QPD X')
    qpdy = device('QPD Y')
    qpdz = device('QPD Z')
    bpd = device('Diff')
    aom = device('AOM')

    
    devs = [counter,counter2,qpdx,qpdy,qpdz,bpd]

    Beep(840,50)
    #Beep(800,50)
    #Beep(780,50)
    #Beep(760,50)
    #Newport Power Meter
    pmeter = pp.via_serial(16)
    pmeter.initialize()
    pmeter.wavelength = 1064
    pmeter.attenuator = True
    pmeter.filter = 'Medium'
    pmeter.go = True
    pmeter.units = 'Watts'


    number_elements = int(timetrace_time/integration_time)

    data = np.zeros([len(devs),number_of_times,number_elements+2]) # The first element will be the power
    
    for m in range(number_of_times):
        i = 0
        for dev in devs:
            # power_aom = 1.5-m*1.5/number_of_spectra
            power_aom = np.polyval(P,laser_powers[m])
            adw.go_to_position([aom],[power_aom])
            dd,ii = adw.get_timetrace_static([dev],duration=timetrace_time,acc=integration_time)
            if m==0:
                time.sleep(1)
            try:
                power = pmeter.data*1000000
            except:
                power = 0
            data[i,m,0] = (str(power))
            data[i,m,1] = str(laser_powers[m])
            data[i,m,2:] = np.array(dd)
            i+=1
            print('633 power %s uW'%(str(laser_powers[m])))
            print('Done with %s'%(dev.properties['Name']))
            print('1064 power %s mW'%(str(power/1000)))
            print('----------------------------------------')
            
    power_aom = np.polyval(P,50) # Sets back the 633 power to a reasonable value
    adw.go_to_position([aom],[power_aom])
    header = "(Trap Power in uW,timetrace) integration time: %f seconds"%(integration_time)
    np.save("%s%s" %(savedir,filename), data)#,fmt='%s', delimiter=",", header=header)
    logger.info('Final file saved as %s%s' %(savedir,filename))
    logger.info('Finished acquiring several sepctra completed')
    Beep(440,200)
    print('Program finish')
