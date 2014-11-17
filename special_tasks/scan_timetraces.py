# Script for acquiring spectra vs intensity of the selected particle

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
from devices.powermeter1830c import powermeter1830c as pp

logger=logger(filelevel=20)

cwd = os.getcwd()
savedir = cwd + '\\' + str(datetime.now().date()) + '\\'
#names of the parameters
par=variables('Par')
fpar=variables('FPar')
data=variables('Data')
fifo=variables('Fifo')

def abort(filename):
    logger = logging.getLogger(get_all_caller())
    logger.critical('You quit!')
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_abort.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    logger.info('Aborted file saved as %s%s_abort.txt' %(savedir,filename))
    sys.exit(0)
        
if __name__ == '__main__': 
    #initialize the adwin and the devices   
    name = input('Give the name of the sample: ')
    cwd = os.getcwd()
    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    i=1
    filename = name
    while os.path.exists(savedir+filename+"_633_raw_image.txt"):
        filename = '%s_%s' %(name,i)
        i += 1
    logger.info('%s\\%s.log' %(savedir,filename))
    print('Data will be saved in %s'%(savedir+filename))
    #init the Adwin programm and also loading the configuration file for the devices
    adw = adq('lib/adbasic/adwin.T99') 
    xpiezo = device('x piezo')
    ypiezo = device('y piezo')
    zpiezo = device('z piezo')
    counter = device('APD 1')
    aom = device('AOM')
    adw.go_to_position([aom],[1])

    #making a 2d scan of the sample and trying to find particles
    xcenter = 44.0 #In um
    ycenter = 59.0
    zcenter = 50.4
    xdim = 5    #In um
    ydim = 5
    xacc = 0.2   #In um
    yacc = 0.2
    devs = [xpiezo,ypiezo,zpiezo]
    # Number of different intensities to acquire time_traces
    number_of_intensities = 10
    #parameters for the refocusing on the particles
    dims = [0.3,0.3,0.6]
    accuracy = [0.05,0.05,0.1]
    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])
    
    
    image = np.array(adw.scan_static(counter,[xpiezo,ypiezo],[xcenter,ycenter],[xdim,ydim],[xacc,yacc]))
    image = np.squeeze(image)
    
    start_scan = np.array([adw.scan_settings[xpiezo.properties['Name']+'_start'] ,adw.scan_settings[ypiezo.properties['Name']+'_start']])
    accuracy_scan = np.array([adw.scan_settings[xpiezo.properties['Name']+'_accuracy'],adw.scan_settings[ypiezo.properties['Name']+'_accuracy']])
   
    #plotting the scan and letting the user select/delete particles
    #also the user has to select a background
    #this is for subtracting its spectra from the spectra of a particle 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    try:
        power = pmeter.data*1000000
    except:
        power = 0
        
    header = 'center = [%s,%s,%s], dim = [%s,%s], acc = [%s,%s], laser = %s uW' %(xcenter,ycenter,zcenter,xdim,ydim,xacc,yacc,power)
    np.savetxt(savedir + "%s_532_raw_image.txt" %(filename),image,fmt='%s',delimiter=',',header=header)
    imshow=ax.imshow(image, interpolation='none', cmap='gnuplot')
    plt.colorbar(imshow)
    plt.savefig(savedir + "%s_532_scan" %(filename))

    plot_backg, = ax.plot([], [],markeredgecolor = 'w' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")      
    try:
        particles=adw.find(adw.scan_image,3)  
        plot_parti, = ax.plot(particles[0,:], particles[1,:],markeredgecolor = 'g' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")
        print('%i particles found automatically'%(len(particles)))
        logger.info('%i particles found automatically'%(len(particles)))
        inter=inter_add_remove(plot_parti,plot_backg,particles[:2,:])
    except:
        logger.warning('no patrticles found')
        plot_parti, = ax.plot([], [],markeredgecolor = 'g' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")
        inter=inter_add_remove(plot_parti,plot_backg)
    ax.set_xlim(0,len(image[0,:]))
    ax.set_ylim(0,len(image[:,0]))
    plt.show()
    
    particles = (inter.particles.T*accuracy_scan+start_scan).T
    background = (inter.background.T*accuracy_scan+start_scan).T
    
    # First make an initial spectra of all the particles
    pressing = input('Enter when spectrometer ready')
    global data 
    data = (np.hstack((particles,background)).T).astype('str')
    data = np.append(np.zeros([len(data),1]).astype('str'),data,1)
    data[:,0] = 'background'
    data[:len(particles[0,:]),0] = 'particle'
    data = np.append(data,np.zeros([len(data),2]).astype('str'),1) 
    
    for i in range(len(particles[0,:])):
        power_aom = 1
        adw.go_to_position([aom],[power_aom]) 
        center = data[i,1:4].astype('float')
        center[2] = zcenter
        adw.go_to_position(devs,center)
        data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=50)
        adw.set_digout(0)           
        time.sleep(0.5)    
        adw.clear_digout(0)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113: #113 is ascii for letter q
                     abort(filename+'_init')
            time.sleep(0.1)
        print('Done with particle %i of %i'%(i+1,len(particles[0,:])))
        for m in range(number_of_intensities):
            power_aom = 1.5-m*1.5/number_of_intensities
            adw.go_to_position([aom],[power_aom])   
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=None)
            try:
                power = pmeter.data*1000000
            except:
                power = 0          
            try:
                data[i,m+4]=str(power)
                data[i,m+5]=np.sum(dd)
            except:
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data[i,m+4]=str(power)
                data[i,m+5]=np.sum(dd)   
            print('Done with %i'%(m))
            
    #make a spectra of the selected background
    for i in range(len(background[0,:])):
        center = np.append(background[:2,i],np.mean(data[:len(particles[0,:]),3].astype('float')))
        adw.go_to_position(devs,center)
        data[i-len(background[0,:]),3]=str(np.mean(data[:len(particles[0,:]),3].astype('float')))
        data[i-len(background[0,:]),4]=str(datetime.now().time())
        adw.set_digout(0)
        time.sleep(0.5)    
        adw.clear_digout(0)
        while adw.get_digin(1):
            if msvcrt.kbhit(): # <--------
                key = msvcrt.getch()
                if ord(key) == 113:
                     abort(filename+'_init')
            time.sleep(0.1)
        print('Done with background %i of %i'%(i+1,len(background[0,:])))
        for m in range(number_of_intensities):
            power_aom = 1.5-m*1.5/number_of_intensities
            adw.go_to_position([aom],[power_aom])   
            dd,ii = adw.get_timetrace_static([counter],duration=1,acc=None)
            try:
                power = pmeter.data*1000000
            except:
                power = 0          
            try:
                data[i,m+4]=str(power)
                data[i,m+5]=np.sum(dd)
            except:
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data = np.append(data,np.zeros([len(data),1]).astype('str'),1)
                data[i,m+4]=str(power)
                data[i,m+5]=np.sum(dd)   
            print('Done with %i'%(m))
    
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s%s_init.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    logger.info('Initial file saved as %s%s_init.txt' %(savedir,filename))
   
    print('Program finished')
