# Script for acquiring timetraces vs intensity with AOM at different points in the sample for each power.
# BIG hipotesis: the sample is homogenous in space.
#
######################### M. Caldarola - May 2016
from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from math import floor
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
import msvcrt
import sys
import os
from lib.logger import get_all_caller,logger
from devices.powermeter1830c import PowerMeter1830c as pp
from winsound import Beep

plt.ion() # enables interactive plot to show big numbers.

########################################################## Here is the info to be filled in before starting
# define parameters for the time trace
timetrace_time = 5# In seconds
integration_time = .05 # In seconds
number_elements = int(timetrace_time/integration_time)
W = 770
## define the array of points to use (absolute position)
origin= [65,65] # um
d=3;     # um
array_size=5;
N=pow(array_size,2)             # number of measurements to be done

X = origin[0]+d*np.linspace(0,array_size-1,array_size)
Y = origin[1]+d*np.linspace(0,array_size-1,array_size)
Z = 47.97 # um
# min and max power seted with the filters. 
# Use the aom from 0 to 10V to controll the power. We measure each point the power with the PowerMeter
V= np.logspace(np.log10(1),np.log10(10),N)
print(V)
print(X)
print(Y)
experiment_label = 'S1607_02_PMMA_film_with_EuComplex_1mM_%snm_power_dependence_origin%s_%sum'%(W,origin[0],origin[1])
print(experiment_label)
input('Press start to begin the measurement.')



# for testing
test = False
###########################################################

# starting

# inizialize

# generate saving path
savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
t = datetime.now().strftime('%Hhs%Mm')

if not os.path.exists(savedir):
    os.makedirs(savedir)
print('Save directory: ' + savedir)

# inizialize the pmeter
try:
    pmeter = pp.via_serial(1)
    pmeter.initialize()
    time.sleep(0.5)

    # set the configuration of power meter.
    pmeter.attenuator = True
    time.sleep(0.5)
    pmeter.wavelength = W
    print('Wavelength = '+str(pmeter.wavelength)+' nm')
    time.sleep(0.5)
    print('Units = '+str(pmeter.units))
    pmeter.range = 0 # set auto scale
    print('Range = '+str(pmeter.range))
    time.sleep(0.5)
except:
    pmeter = 0
    print('Problem with Power Meter')

# inizialize adwin
adw = adq(model='goldII')
xpiezo = device('x piezo')
ypiezo = device('y piezo')
zpiezo = device('z piezo')
devs = [xpiezo,ypiezo,zpiezo]
counter1 = device('APD 1')
counter2 = device('APD 2')
aom = device('AOM Ti:Sa')

# inizialize the vectors needed
pw =np.zeros((1,N)) # power at bfp
data=np.zeros((2,N))
edata = np.zeros((2,N))
bkg=np.zeros((2,N))
ebkg = np.zeros((2,N))


# while in the measurement
n=0
input('Close the shutter and press enter.')
if test==False:
    filename_p = experiment_label +'_Meas_at_'+t+'_dark.dat'
    dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
    header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
    np.savetxt("%s%s" %(savedir,filename_p), dd,fmt='%s', delimiter=",", header=header)

input('Open the shutter and press enter.')


print('Start the while')

while n <N:
    print('Power number'+str(n+1)+'out of'+str(N))
    # set power with aom
    adw.go_to_position([aom],[V[n]])
    print('Curent voltage='+str(V[n]))
    # measure power
    pw_now=(pmeter.data*1000000)
    pw[0,n]=pw_now/9 # power at bfp
    print('Measured Power =%s uW'%(str(pw_now)))
    
    filename_p = experiment_label +'_Meas_at_'+t+'_Measured_Power='+str(pw_now)+'uW.dat'
    print(filename_p)
    ## move to the next position
    ind = np.unravel_index(n,[array_size,array_size])
    adw.go_to_position(devs,[X[ind[0]],Y[ind[1]],Z])
    
    # # time trace and save 
    print('Taking time trace')
    if test==False:
        dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
         # append data 
        data[:,n]=np.mean(dd,axis=1)/integration_time
        edata[:,n]=np.std(dd,axis=1)/integration_time
    print('Ended time trace')
   
    if test==False: # save timetrace 
        header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
        np.savetxt("%s%s" %(savedir,filename_p), dd,fmt='%s', delimiter=",", header=header)
    print('Power finished')
    n=n+1
        

# finalize power meter
pmeter.finalize()   


if test==False:
    header2 = "Power (uW), Avg counter1 (cps),Avg counter2 (cps), Std counter1 (cps), std counter2 (cps)"
    np.savetxt("%s%s" %(savedir,experiment_label +'_Meas_at_'+t+'_averaged.dat'),  np.concatenate((np.transpose(pw),np.transpose(data),np.transpose(edata)),axis=1),fmt='%s', delimiter=",", header=header2)    
    
    

    
# plot 
plt.figure()
p1=plt.errorbar(pw[0,:],data[0,:],yerr=edata[0,:], fmt='o')
p2=plt.errorbar(pw[0,:],data[1,:],yerr=edata[1,:], fmt='o')
plt.setp(p1,color='r',linewidth='2')
plt.setp(p2,color='b',linewidth='2')
plt.xlabel('Power [uW]')
plt.ylabel('Mean counts in %s'%integration_time)
plt.show()


input('Press enter to finish')
print('End')




