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
pmeter = pp.via_serial(1)
pmeter.initialize()
time.sleep(0.5)

# set the configuration of power meter.
pmeter.attenuator = False
time.sleep(0.5)
pmeter.wavelength = 671
print('Wavelength = '+str(pmeter.wavelength)+' nm')
time.sleep(0.5)
print('Units = '+str(pmeter.units))
pmeter.range = 0
print('Range = '+str(pmeter.range))
time.sleep(0.5)

# inizialize adwin
adw = adq()
xpiezo = device('x piezo')
ypiezo = device('y piezo')
zpiezo = device('z piezo')
counter1 = device('APD 1')
counter2 = device('APD 2')

# define parameters for the time trace
timetrace_time = 0.5 # In seconds
integration_time = .01 # In seconds
number_elements = int(timetrace_time/integration_time)

N=3
Pmax = 250 # uw

# inizialize
pw =np.zeros((1,N))
data=np.zeros((2,N))
edata = np.zeros((2,N))


# for in the measurement
for n in range(N):
    print('N measurement =%s. Power to be set= %s uW'%(str(n),str(np.linspace(0,Pmax,N)[n])))
    input('&&&&&&&&&&&&&& Press enter to launch the measurement.')
    pw_now=(pmeter.data*1000000)
    #pw.append(pw_now)
    pw[0,n]=pw_now
    print('Measured Power =%s uW'%(str(pw_now)))
    filename = 'M'+t+'_TimeTrace_Power='+str(pw_now)+'uW.dat'
    print('Taking time trace')
    dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
    print('Ended time trace')

    data[:,n]=np.mean(dd,axis=1)
    edata[:,n]=np.std(dd,axis=1)

    header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
    np.savetxt("%s%s" %(savedir,filename), dd,fmt='%s', delimiter=",", header=header)
    Beep(440,200)

# finalize power meter
pmeter.finalize()   



header2 = "(Power (uW), Avg counter1 (counts),Avg counter2 (counts), Std counter1 (counts), std counter1 (counts)"
np.savetxt("%s%s" %(savedir,'M'+t+'_averaged.dat'),  np.concatenate((np.transpose(pw),np.transpose(data),np.transpose(edata)),axis=1),fmt='%s', delimiter=",", header=header2)    

# plot 
plt.figure()
p1 =plt.errorbar(pw[0,:],data[0,:],yerr=edata[0,:], fmt='o')
p2=plt.errorbar(pw[0,:],data[1,:],yerr=edata[1,:], fmt='o')
plt.setp(p1,color='r',linewidth='2')
plt.setp(p2,color='b',linewidth='2')
plt.xlabel('Power [uW]')
plt.ylabel('Mean counts [cps]')
plt.show()
  

print('End')




