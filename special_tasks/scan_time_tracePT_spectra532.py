from __future__ import division
import numpy as np
import time
import matplotlib.pyplot as plt
from lib.adq_mod import *
from lib.xml2dict import device,variables
from datetime import datetime
from tkinter.filedialog import askopenfilename
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
    lockin = device('Lock-in')
    
    #Newport Power Meter
    pmeter = pp(0)
    pmeter.initialize()
    pmeter.wavelength = 633
    pmeter.attenuator = True
    pmeter.filter = 'Medium' 
    pmeter.go = True
    pmeter.units = 'Watts' 
    
    #Using bright particle to focus
    init_xcenter = 50.9 #In um
    init_ycenter = 52.32
    init_zcenter = 54.20
    init_center = [init_xcenter, init_ycenter, init_zcenter]
    devs = [xpiezo,ypiezo,zpiezo]
    timetrace_time = 5 # In seconds
    integration_time = .02 # In seconds
    number_elements = int(timetrace_time/integration_time)
    
    #parameters for the refocusing on the particles
    dims = [0.3,0.3,0.6]
    accuracy = [0.05,0.05,0.1]
    [init_xcenter, init_ycenter, init_zcenter] = adw.focus_full(lockin,devs,init_center,dims,accuracy,rate=1,speed=50)
    zcenter = init_zcenter
    init_center = [init_xcenter, init_ycenter, init_zcenter] 
    xcenter = 50
    ycenter = 50
    
    # Dimension of the scan
    xdim = 20    #In um
    ydim = 20
    xacc = 0.1   #In um
    yacc = 0.1

    adw.go_to_position(devs[:3],[xcenter,ycenter,zcenter])
       
    print('First let\'s do a scan with the 633nm laser and PhotoThermal')
    
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
    np.savetxt(savedir + "%s_633_raw_image.txt" %(filename),image,fmt='%s',delimiter=',',header=header)
    imshow=ax.imshow(image, interpolation='none', cmap='gnuplot')
    plt.colorbar(imshow)
    plt.savefig(savedir + "%s_633_scan" %(filename))

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
    
    # First take time-traces with the lockin
    
    print('Starting to take timetraces with the lock-in')
    global data 
    data = (np.hstack((particles,background)).T).astype('str')
    data = np.append(np.zeros([len(data),1]).astype('str'),data,1)
    data[:,0] = 'background'
    data[:len(particles[0,:]),0] = 'particle'
    data = np.append(data,np.zeros([len(data),2]).astype('str'),1) 
    time_traces = np.zeros([len(data),number_elements])
    
    
    for i in range(len(particles[0,:])):
        center = data[i,1:4].astype('float')
        center[2] = zcenter
        adw.go_to_position(devs,center)
        data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=50)
        adw.set_digout(0)           
        time.sleep(0.5)    
        adw.clear_digout(0)               
        dd,ii = adw.get_timetrace_static([lockin],duration=timetrace_time,acc=integration_time)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113:
                    abort(filename + '_inter')
            time.sleep(0.1)
        time_traces[i,:] = np.array(dd)
        print('Done with particle %i of %i'%(i+1,len(particles[0,:])))
    print('633 PhotoThermal time Traces taken')
    
    #make timetraces of the selected background
    for i in range(len(background[0,:])):
        center = np.append(background[:2,i],np.mean(data[:len(particles[0,:]),3].astype('float')))
        adw.go_to_position(devs,center)
        adw.set_digout(0)           
        time.sleep(0.5)    
        adw.clear_digout(0)               
        dd,ii = adw.get_timetrace_static([lockin],duration=timetrace_time,acc=integration_time)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113:
                    abort(filename + '_inter')
            time.sleep(0.1)        
        time_traces[i+len(particles[0,:]),:] = np.array(dd)
        print('Done with background %i of %i'%(i+1,len(background[0,:])))

        
    header = "Time Traces with Lock-In. Duration = %s seconds. Integration time = %s seconds"%(timetrace_time,integration_time)
    np.savetxt("%s%s_time_trace.txt" %(savedir,filename), time_traces,fmt='%s', delimiter=",", header=header)   
    logger.info('Time traces file saved as %s%s_time_trace.txt' %(savedir,filename))

    header = "Coordinate of the particles"
    np.savetxt("%s%s_coordinates.txt" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)   
    
    print('Now is time to acquire spectra with the 532nm laser')
    print('Change to 532nm notch before the spectrometer and APD')
    print('Remove 633nm filters')
    pressing = input('Setup the spectrometer and press enter when ready')
    
    
    [init_xcenter, init_ycenter, init_zcenter] = adw.focus_full(lockin,devs,init_center,dims,accuracy,rate=1,speed=50)
    z_center = init_zcenter
    
    
    num_particles = sum(data[:,0]=='particle')
    num_background = sum(data[:,0]=='background')
    

    
    for i in range(num_particles):
        center = data[i,1:4].astype('float')
        center[2] = zcenter
        adw.go_to_position(devs,center)
        adw.focus_full(counter,devs,center,dims,accuracy).astype('str')
        adw.set_digout(0)           
        time.sleep(0.5)    
        adw.clear_digout(0)
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113:
                    abort(filename + '_inter')
            time.sleep(0.1)               
        print('Acquired spectra of particle %i'%(i))
    
    for i in range(num_background):
        center = np.append(background[:2,i],np.mean(data[:len(particles[0,:]),3].astype('float')))
        adw.go_to_position(devs,center)  
        adw.set_digout(0)           
        time.sleep(0.5)    
        adw.clear_digout(0)        
        while adw.get_digin(1):
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if ord(key) == 113:
                     abort(filename + '_inter')
            time.sleep(0.1)
        print('Acquired background %i'%(i))  
    print('Done with the 532')
    print('Program finish')
