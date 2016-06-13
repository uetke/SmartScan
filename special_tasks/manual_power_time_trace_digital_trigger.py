# Script for acquiring timetraces vs intensity manually
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
timetrace_time = 10# In seconds
integration_time = .05 # In seconds
number_elements = int(timetrace_time/integration_time)
W = 770
# parameters for refocus
experiment_label = 'S1605_14_Tisa%snm_solution'%(W)
print(experiment_label)
input('Cont')
N=10             # number of measurements to be done
# min and max power to use in the sample (make sure it is lower than the threshold)
# it is transformed to the power to be measured automatically.
Pmin = 200
Pmax = 3000 # uw at BFP
pw_to_set= np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)

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
    self.pmeter = 0
    print('Problem with Power Meter')

# inizialize adwin
adw = adq(model='goldII')

counter1 = device('APD 1')
counter2 = device('APD 2')

# inizialize the vectors needed
pw =np.zeros((1,N)) # power at bfp
data=np.zeros((2,N))
edata = np.zeros((2,N))
bkg=np.zeros((2,N))
ebkg = np.zeros((2,N))


# while in the measurement
n=0
print('First Measurement. Power to be set= %s uW'%(pw_to_set[n]))
print('Waiting for triggger...')

# shows a plot with the number to be set in big fontsize
fig = plt.figure()
ax = fig.add_subplot(111)
ax.text(0,0.5,'P =%.2e'%(pw_to_set[n])+' uW',fontsize=55)
plt.show()
plt.pause(0.0001)
print('Waiting for signal...')

while n <N:

    if adw.get_digin(0):
        plt.close()
        print('Measurement started.')
        Beep(440,800)
               
        pw_now=(pmeter.data*1000000)
        pw[0,n]=pw_now/9 # power at bfp
        print('Measured Power =%s uW'%(str(pw_now)))
        
        filename_p = experiment_label +'_Meas_at_'+t+'_TimeTrace_Power='+str(pw_now)+'uW.dat'
        # # time trace and save on the particle
        print('Taking time trace')
        dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
        print('Ended time trace')
        # append data 
        data[:,n]=np.mean(dd,axis=1)/integration_time
        edata[:,n]=np.std(dd,axis=1)/integration_time
        if test==False: # save timetrace 
            header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
            np.savetxt("%s%s" %(savedir,filename_p), dd,fmt='%s', delimiter=",", header=header)
        
        Beep(440,250)
        Beep(560,250)
        Beep(440,250)
        Beep(440,350)
        
        n=n+1
        if n < N:
            print('Measurement number =%s out of %s. Power to be set= %s uW'%(n+1,N,np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)[n]))
            print('Waiting for trigger...') 
            # show a new plot with the next value to be set
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.text(0,0.5,'P =%.2e'%(pw_to_set[n])+' uW',fontsize=55)
            ax.text(0,0.9,'N =%s'%(n)+' out of %s'%(N),fontsize=55)
            plt.show()
            plt.pause(0.0001)
        

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




