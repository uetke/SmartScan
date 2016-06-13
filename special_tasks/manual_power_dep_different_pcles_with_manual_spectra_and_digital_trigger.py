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

# parameters for refocus
experiment_label = 'S1606_06_EuComplex_1mM_770nm_power_depe'
pcle1 = [45.89, 42.02, 49.47]
pcle2 = [50.82, 46.90, 49.47]
pcle3 = [54.91, 46.35, 49.47]
pcle4 = [44.38, 48.88, 49.47]
pcle5 = [54.61, 57.60, 49.47]

# Create array of particles
particles = []
particles.append(pcle1)
particles.append(pcle2)
particles.append(pcle3)
particles.append(pcle4)
particles.append(pcle5)


dims = [0.5,0.5,0.8]
accuracy = [0.05,0.05,0.1]

N=2             # number of measurements to be done
# min and max power to use in the sample (make sure it is lower than the threshold)
# it is transformed to the power to be measured automatically.
Pmin = 500
Pmax = 1000 # uw at BFP
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
    pmeter.wavelength = 770
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

# inizialize the vectors needed
pw =np.zeros((1,N)) # power at bfp
data=np.zeros((2,N))
edata = np.zeros((2,N))
bkg=np.zeros((2,N))
ebkg = np.zeros((2,N))

## measure dark

# # time trace and save on the particle
input('close the shutter for the laser and press enter to take an initial time trace of dark counts')
dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
filename_p = experiment_label +'_Meas_at_'+t+'_TimeTrace_dark.dat'
if test==False: # save timetrace plce
    header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
    np.savetxt("%s%s" %(savedir,filename_p), dd,fmt='%s', delimiter=",", header=header)

input('take a dark spectra (label as 00) and then press enter...')


    
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
    sleep(0.1)
    if adw.get_digin(0):
        plt.close()
        print('Measurement started.')
        Beep(440,200)
        for nn in range(len(particles)):
            # go to the particle 
            if test==False:
                print('going to pcle')
                adw.go_to_position(devs,particles[nn])
                time.sleep(0.1)
                print('PCLE position = '+str(particles[nn])+'um')
            
            pw_now=(pmeter.data*1000000)
            pw[0,n]=pw_now/9 # power at bfp
            print('Measured Power =%s uW'%(str(pw_now)))
            
            filename_p = experiment_label +'_Meas_at_'+t+'_TimeTrace_Pcle'+str(nn)+'_Measured_Power='+str(pw_now)+'uW.dat'
            filename_b = experiment_label +'_Meas_at_'+t+'_TimeTrace_Bkg'+str(nn)+'_Measured_Power='+str(pw_now)+'uW.dat'
            # # time trace and save on the particle
            print('Started time trace on the particle '+str(nn))
            dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
            print('Ended time trace on the particle '+str(nn))

            # append data pcle
            if nn==1:
                data[:,n]=np.mean(dd,axis=1)/integration_time
                edata[:,n]=np.std(dd,axis=1)/integration_time
            if test==False: # save timetrace plce
                header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
                np.savetxt("%s%s" %(savedir,filename_p), dd,fmt='%s', delimiter=",", header=header)
            ## spectra
            input('take the spectra on the PCLE' + str(nn)+ 'and THEN press enter to continue...')
            
            
            
            # # time trace and save BKG
            print('Going to the BKG Position')
            if test==False:
                bkg_position = [particles[nn][0]+2,particles[nn][1]+2,particles[nn][2]]
                print('BKG position = '+str(bkg_position)+'um')
                adw.go_to_position(devs,bkg_position)
                time.sleep(0.1)
            print('Started time trace on the BKG '+str(nn))
            dd,ii = adw.get_timetrace_static([counter1,counter2],duration=timetrace_time,acc=integration_time)
            print('Ended time trace on the BKG '+str(nn))
            # append data bgg
            if nn==1:
                bkg[:,n]=np.mean(dd,axis=1)/integration_time
                ebkg[:,n]=np.std(dd,axis=1)/integration_time
            if test==False:
                header = "(Row1: TimeTrace1 (counts), Row2: TimeTrace1 (counts)) integration time: %f seconds"%(integration_time)
                np.savetxt("%s%s" %(savedir,filename_b), dd,fmt='%s', delimiter=",", header=header)
            input('take the spectra on the BKG' + str(nn)+ 'and then press enter to continue...')
            print('done with this PARTICLE at this power')
            print('------------------------')
            
        Beep(440,250)
        Beep(560,250)
        Beep(440,250)
        Beep(440,350)
        print('Done with this power, go to next')
        
        n=n+1
        if n < N:
            print('Measurement number =%s out of %s. Power to be set= %s uW'%(n+2,N,np.logspace(np.log10(Pmin*9),np.log10(Pmax*9),N)[n]))
            print('Waiting for trigger...') 
            # show a new plot with the next value to be set
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.text(0,0.5,'P =%.2e'%(pw_to_set[n])+' uW',fontsize=55)
            plt.show()
            plt.pause(0.0001)
        

# finalize power meter
pmeter.finalize()   


if test==False:
    header2 = "Power (uW), Avg counter1 (cps),Avg counter2 (cps), Std counter1 (cps), std counter2 (cps)"
    np.savetxt("%s%s" %(savedir,experiment_label +'_Meas_at_'+t+'_Pcle_1_averaged.dat'),  np.concatenate((np.transpose(pw),np.transpose(data),np.transpose(edata)),axis=1),fmt='%s', delimiter=",", header=header2)    
    np.savetxt("%s%s" %(savedir,experiment_label +'_Meas_at_'+t+'_Bkg_1_averaged.dat'),  np.concatenate((np.transpose(pw),np.transpose(bkg),np.transpose(ebkg)),axis=1),fmt='%s', delimiter=",", header=header2)    
    
    #header3 = "pw (uW), xp (um), yp (um), zp (um),"
    #np.savetxt("%s%s" %(savedir,experiment_label +'_Meas_at_'+t+'_Final_Pcle_position.dat'),  np.concatenate((np.transpose(pw),np.transpose(xp),np.transpose(yp),np.transpose(zp)),axis=1),fmt='%s', delimiter=",", header=header3)    
    
    

    
# plot 
plt.figure()
p1=plt.errorbar(pw[0,:],data[0,:],yerr=edata[0,:], fmt='o')
p2=plt.errorbar(pw[0,:],data[1,:],yerr=edata[1,:], fmt='o')
plt.setp(p1,color='r',linewidth='2')
plt.setp(p2,color='b',linewidth='2')
plt.xlabel('Power [uW]')
plt.ylabel('Mean counts in %s'%integration_time)

#plt.figure()
#plt.plot(np.array(range(N)),np.squeeze(xp,axis=0),'bo')
#plt.plot(np.array(range(N)),np.squeeze(yp,axis=0),'ro')
#plt.plot(np.array(range(N)),np.squeeze(zp,axis=0),'s')
#plt.xlabel('N')
#plt.ylabel('Position in uw')




plt.show()
input('Press enter to finish')
print('End')




