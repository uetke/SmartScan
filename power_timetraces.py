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
        # plt.plot(intensity,AOM_voltage,'.')
        # plt.plot(intensity,np.polyval(P,intensity))
        # plt.ylabel('AOM voltage (V)')
        # plt.xlabel('Laser intensity (uW)')
        # plt.show()
    else:
        raise Exception('The AOM was not calibrated today, please do it before running this program...')

    number_of_times = 10
    laser_min = 10 # In uW
    laser_max = 150 # In uW
    laser_powers = np.linspace(laser_min,laser_max,number_of_times)

    #initialize the adwin and the devices
    name = 'power_intensity'

    i=1
    filename = '%s_%s.dat'%(name,i)
    while os.path.exists(savedir+filename):
        i += 1
        filename = '%s_%s.dat' %(name,i)

    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s'%(savedir+filename))
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq()
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    aom = device('AOM')

    devs = [xpiezo,ypiezo,zpiezo]

    Beep(840,200)
    #Newport Power Meter
    pmeter = pp.via_serial(1)
    pmeter.initialize()
    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.filter = 'Medium'
    pmeter.go = True
    pmeter.units = 'Watts'

    timetrace_time = 2 # In seconds
    integration_time = .01 # In seconds
    number_elements = int(timetrace_time/integration_time)

    data = np.zeros([number_of_times*2,number_elements+1]) # The first element will be the power

    for m in range(number_of_times):
        # power_aom = 1.5-m*1.5/number_of_spectra
        power_aom = np.polyval(P,laser_powers[m])
        adw.go_to_position([aom],[power_aom])
        dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
        if m==0:
            time.sleep(1)
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        data[m,0] = (str(power))
        data[m,1:] = np.array(dd)
        print('Power %s uW'%(str(power)))
        print('Done with %i'%(m))

    for m in range(number_of_times):
        # power_aom = 1.5-m*1.5/number_of_spectra
        power_aom = np.polyval(P,laser_powers[-m-1])
        adw.go_to_position([aom],[power_aom])
        dd,ii = adw.get_timetrace_static([counter],duration=timetrace_time,acc=integration_time)
        if m==0:
            time.sleep(1)
        try:
            power = pmeter.data*1000000
        except:
            power = 0
        data[number_of_times+m,0] = (str(power))
        data[number_of_times+m,1:] = np.array(dd)
        print('Power %s uW'%(str(power)))
        print('Done with %i'%(number_of_times-m))



    header = "(Power in uW,timetrace) integration time: %f seconds"%(integration_time)
    np.savetxt("%s%s" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Final file saved as %s%s' %(savedir,filename))
    logger.info('Finished acquiring several sepctra completed')
    Beep(440,200)
    print('Program finish')
