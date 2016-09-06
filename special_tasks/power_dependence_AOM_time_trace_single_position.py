#
#
#
#
######################### M. Caldarola - April 2016
import numpy as np
from devices.powermeter1830c import PowerMeter1830c as pp
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables


########################################################## Here is the info to be filled in before starting
# define parameters for the time trace
timetrace_time = 1# In seconds
integration_time = .05 # In seconds
number_elements = int(timetrace_time/integration_time)
W = 785
Npts=2
# min and max power seted with the filters. 
# Use the aom from 0 to 10V to controll the power. We measure each point the power with the PowerMeter
Vaom= np.logspace(np.log10(1),np.log10(10),Npts)

Sample = 'Test'
experiment_label = sample+'_%snm_power_dependence_'%(W)
print(experiment_label)
input('Press start to begin the measurement.')




# for testing
test = False
###########################################################
# save folder 

# generate saving path
savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
t = datetime.now().strftime('%Hhs%Mm')
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

# set the configuration of power meter.
pmeter.attenuator = True
time.sleep(0.5)
pmeter.wavelength = W
print('Wavelength = '+str(pmeter.wavelength)+' nm')
time.sleep(0.5)
print('Units = '+str(pmeter.units))
pmeter.range = 0
print('Range = '+str(pmeter.range))
time.sleep(0.5)

# inizialize adwin
adw = adq(model='goldII')
xpiezo = device('x piezo')
ypiezo = device('y piezo')
zpiezo = device('z piezo')
devs = [xpiezo,ypiezo,zpiezo]
counter1 = device('APD 1')
counter2 = device('APD 2')
aom = device('AOM Ti:Sa')
# turn off
adw.go_to_position([aom],[0.01])
time.sleep(1)


# for to get the data
pw = [];
data=[]
edata = []

print('Runnin the for...')

for a in Vaom:
    print('Voltage to be set ' + str(a))
    adw.go_to_position([aom],[a])
    time.sleep(1)
    pw_now=pmeter.data*1000000 # the data is now in uW
    pw.append(pw_now) 
    print('Taking time trace')
    if test==False:
        dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
         # append data 
        data.append(np.mean(dd,axis=1)/integration_time)
        edata.append(np.std(dd,axis=1)/integration_time)
    print('Ended time trace')
    filename = experiment_label+'time_trace_pw_bfp_'+srt(pw_now/9)+'uW.dat'
    if test==False: # save timetrace 
        header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
        np.savetxt("%s%s" %(savedir,filename), dd,fmt='%s', delimiter=",", header=header)
    print('Power finished')
    
print('For done!')

# finalize
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


print('Finished')


