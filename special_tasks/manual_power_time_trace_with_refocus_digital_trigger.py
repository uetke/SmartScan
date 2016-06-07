# Script for acquiring timetraces vs intensity manually
#
######################### M. Caldarola - April 2016
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
    pmeter.attenuator = False
    time.sleep(0.5)
    pmeter.wavelength = 532
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
xpiezo = device('x piezo')
ypiezo = device('y piezo')
zpiezo = device('z piezo')
devs = [xpiezo,ypiezo,zpiezo]
counter1 = device('APD 1')
counter2 = device('APD 2')

# define parameters for the time trace
timetrace_time = 2# In seconds
integration_time = .05 # In seconds
number_elements = int(timetrace_time/integration_time)

# parameters for refocus
experiment_label = 'Scattering_532nm'
devs = [xpiezo,ypiezo,zpiezo]
center = [46.58,49.38,50.40]
dims = [0.4,0.4,0.8]
accuracy = [0.05,0.05,0.1]
    

N=10# number of measurements to be done

# min and max power to use in the sample (make sure it is lower than the threshold)
# it is transformed to the power to be measured automatically.
Pmin = 0.01
Pmax = 0.3 # uw

# inizialize
pw =np.zeros((1,N)) # power at bfp
data=np.zeros((2,N))
edata = np.zeros((2,N))
bkg=np.zeros((2,N))
ebkg = np.zeros((2,N))

xp = np.zeros((1,N)) # position
yp = np.zeros((1,N)) # position
zp = np.zeros((1,N)) # position

# for test
test = False

# while in the measurement
n=0
print('First Measurement. Power to be set= %s uW'%(np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)[n]))
print('Waiting for triggger...')
while n <N:

    if adw.get_digin(0):
        print('Measurement started.')
        Beep(440,200)
        # refocus 
        if test==False:
            print('Refocusing on pcle')
            position = adw.focus_full(counter1,devs,center,dims,accuracy).astype('str')
            xp[0,n]=position[0]
            yp[0,n]=position[1]
            zp[0,n]=position[2]
            time.sleep(0.1)
            print('Final Plce position = %s um'%(position))
        
        pw_now=(pmeter.data*1000000)
        pw[0,n]=pw_now/9 # power at bfp
        print('Measured Power =%s uW'%(str(pw_now)))
        
        filename_p = experiment_label +'Meas_at_'+t+'_TimeTrace_Pcle_Power='+str(pw_now)+'uW.dat'
        filename_b = experiment_label +'Meas_at_'+t+'_TimeTrace_Bkg_Power='+str(pw_now)+'uW.dat'
        # # time trace and save on the particle
        print('Taking time trace on the particle')
        dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
        print('Ended time trace on the particle')
        # append data pcle
        data[:,n]=np.mean(dd,axis=1)/integration_time
        edata[:,n]=np.std(dd,axis=1)/integration_time
        if test==False: # save timetrace plce
            header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
            np.savetxt("%s%s" %(savedir,filename_p), dd,fmt='%s', delimiter=",", header=header)
        
        # # time trace and save BKG
        print('Taking time trace BKG')
        if test==False:
            bkg_position = [xp[0,n]+1,yp[0,n]+1,zp[0,n]]
            print('BKG position = '+str(bkg_position)+'um')
            adw.go_to_position(devs,bkg_position)
            time.sleep(0.1)
        dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
        print('Ended time trace BKG')
        # append data bgg
        bkg[:,n]=np.mean(dd,axis=1)/integration_time
        ebkg[:,n]=np.std(dd,axis=1)/integration_time
        if test==False:
            header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
            np.savetxt("%s%s" %(savedir,filename_b), dd,fmt='%s', delimiter=",", header=header)

        Beep(440,200)
        Beep(560,200)
        Beep(440,200)
        
        n=n+1
        if n < N:
            print('Measurement number =%s out of %s. Power to be set= %s uW'%(n+1,N,np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)[n]))
            print('Waiting for trigger...')
        

# finalize power meter
pmeter.finalize()   


if test==False:
    header2 = "(Power (uW), Avg counter1 (cps),Avg counter2 (cps), Std counter1 (cps), std counter1 (cps)"
    np.savetxt("%s%s" %(savedir,experiment_label +'Meas_at_'+t+'_Pcle_averaged.dat'),  np.concatenate((np.transpose(pw),np.transpose(data),np.transpose(edata)),axis=1),fmt='%s', delimiter=",", header=header2)    
    np.savetxt("%s%s" %(savedir,experiment_label +'Meas_at_'+t+'_Bkg_averaged.dat'),  np.concatenate((np.transpose(pw),np.transpose(bkg),np.transpose(ebkg)),axis=1),fmt='%s', delimiter=",", header=header2)    

    
# plot 
plt.figure()
p1=plt.errorbar(pw[0,:],data[0,:],yerr=edata[0,:], fmt='o')
p2=plt.errorbar(pw[0,:],data[1,:],yerr=edata[1,:], fmt='o')
plt.setp(p1,color='r',linewidth='2')
plt.setp(p2,color='b',linewidth='2')
plt.xlabel('Power [uW]')
plt.ylabel('Mean counts in %s'%integration_time)

plt.figure()
plt.plot(np.array(range(N)),np.squeeze(xp,axis=0),'bo')
plt.plot(np.array(range(N)),np.squeeze(yp,axis=0),'ro')
plt.plot(np.array(range(N)),np.squeeze(zp,axis=0),'s')
plt.xlabel('N')
plt.ylabel('Position in uw')

plt.show()



print('End')




