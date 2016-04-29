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
t = datetime.now().strftime('%H_%M')
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
    pmeter.wavelength = 759
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
counter1 = device('APD 1')
counter2 = device('APD 2')

# define parameters for the time trace
timetrace_time = 15 # In seconds
integration_time = .05 # In seconds
number_elements = int(timetrace_time/integration_time)

# parameters for refocus
devs = [xpiezo,ypiezo,zpiezo]
center = [56.64,53.73,51.35]
dims = [0.4,0.4,0.8]
accuracy = [0.05,0.05,0.1]
    

N=1# number of measurements to be done
# min and max power to be measured (make sure it is lower than the threshold)

Pmin = 150
Pmax = 250 # uw

# inizialize
pw =np.zeros((1,N)) # power at bfp
data=np.zeros((2,N))
edata = np.zeros((2,N))
xp = np.zeros((1,N)) # position
yp = np.zeros((1,N)) # position
zp = np.zeros((1,N)) # position

# for test
test = False

# for in the measurement
for n in range(N):
    print('N measurement =%s / %s. Power to be set= %s uW'%(n,N,np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)[n]))
    input('&&&&&&&&&&&&&& Press enter to launch the measurement.')
    # refocus 
    if test==False:
        position = adw.focus_full(counter1,devs,center,dims,accuracy).astype('str')
        xp[0,n]=position[0]
        yp[0,n]=position[1]
        zp[0,n]=position[2]
        time.sleep(0.1)
        print('Position = %s um'%(position))
        
    pw_now=(pmeter.data*1000000)
    #pw.append(pw_now)
    pw[0,n]=pw_now/9 # power at bfp
    print('Measured Power =%s uW'%(str(pw_now)))
    filename = 'M'+t+'_TimeTrace_Power='+str(pw_now)+'uW.dat'
    print('Taking time trace')
    dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
    print('Ended time trace')

    data[:,n]=np.mean(dd,axis=1)/integration_time
    edata[:,n]=np.std(dd,axis=1)/integration_time
    if test==False:
        header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
        np.savetxt("%s%s" %(savedir,filename), dd,fmt='%s', delimiter=",", header=header)
    Beep(440,500)
    Beep(560,500)

# finalize power meter
pmeter.finalize()   


if test==False:
    header2 = "(Power (uW), Avg counter1 (cps),Avg counter2 (cps), Std counter1 (cps), std counter1 (cps)"
    np.savetxt("%s%s" %(savedir,'M'+t+'_averaged.dat'),  np.concatenate((np.transpose(pw),np.transpose(data),np.transpose(edata)),axis=1),fmt='%s', delimiter=",", header=header2)    

# plot 
# plt.figure()
# p1=plt.errorbar(pw[0,:],data[0,:],yerr=edata[0,:], fmt='o')
# p2=plt.errorbar(pw[0,:],data[1,:],yerr=edata[1,:], fmt='o')
# plt.setp(p1,color='r',linewidth='2')
# plt.setp(p2,color='b',linewidth='2')
# plt.xlabel('Power [uW]')
# plt.ylabel('Mean counts in %s'%integration_time)

# plt.figure()
# plt.plot(np.array(range(N)),np.squeeze(xp,axis=0),'bo')
# plt.plot(np.array(range(N)),np.squeeze(yp,axis=0),'ro')
# plt.plot(np.array(range(N)),np.squeeze(zp,axis=0),'s')
# plt.xlabel('N')
# plt.ylabel('Position in uw')

# plt.show()



print('End')




