"""
    spectra_scan_white_light.py
    -------------
    Loads a scan and takes spectra of several particles, including background.

    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl

"""
import numpy as np
import time
import msvcrt
import sys
import os
from datetime import datetime
import pickle
import re # Regular expression, to extract the coordinates from the image
from experiment import *
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
from lib.adq_mod import inter_add_remove


if __name__ == '__main__':

    z = 50.8 # Need to define manually since it is not stored in the scan (yet)
    # Initialize the class for the experiment
    exp = experiment()

    # Loads the file
    filename = askopenfilename(initialdir='D:\\Data')
    f = open(filename,'r')
    # Extracts the center and accuracy of the image
    for i in range(4):
        A = f.readline()

    C = re.findall(r'\d+\.\d+',A)
    accuracy_scan = np.array([C[4],C[5]]).astype('float')
    start_scan = np.array([C[0],C[1]]).astype('float')
    len_scan = np.array([C[2],C[3]]).astype('float')

    start_scan = start_scan - len_scan/2

    image = np.loadtxt(filename,dtype='bytes',delimiter=',').astype('float')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    imshow=ax.imshow(image, interpolation='none', cmap='gnuplot')
    plt.colorbar(imshow)

    plot_backg, = ax.plot([], [],markeredgecolor = 'w' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")
    try:
        particles=exp.adw.find(image,3)
        plot_parti, = ax.plot(particles[0,:], particles[1,:],markeredgecolor = 'g' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")
        print('%i particles found automatically'%(len(particles)))
        inter=inter_add_remove(plot_parti,plot_backg,particles[:2,:])
    except:
        plot_parti, = ax.plot([], [],markeredgecolor = 'g' ,marker='$\circ$',markersize=10,markeredgewidth=2.0,linestyle="")
        inter=inter_add_remove(plot_parti,plot_backg)
    ax.set_xlim(0,len(image[0,:]))
    ax.set_ylim(0,len(image[:,0]))
    plt.show()
    pcl = (inter.particles.T*accuracy_scan+start_scan)
    bkg = (inter.background.T*accuracy_scan+start_scan)

    data = (np.hstack((pcl.T,bkg.T)).T).astype('str')
    data = np.append(np.zeros([len(data),1]).astype('str'),data,1)
    data[:,0] = 'background'
    header = "type,x-pos,y-pos,z-pos,first scan time" + ",time_%s"*(len(data[0,:])-5) %tuple(range((len(data[0,:])-5)))
    np.savetxt("%s_particles.txt" %(filename), data,fmt='%s', delimiter=",", header=header)

    # Create array of particles
    particles = []
    pcle = 'pcle'
    # # Coordinates of the particles
    for i in range(len(pcl)):
        coord = [pcl[i][0], pcl[i][1], z]
        particles.append(particle(coord,pcle,i))

    coord = [bkg[0][0], bkg[0][1], z]

    background = particle(coord,'bkg',1)

    exp.number_of_accumulations = 1 # Accumulations of each spectra (for reducing noise in long-exposure images)
    # Wavelengths for the acquisition at different central positions.
    spec_wl = [650, 650] # Minimum and maximum of the central wavelength
    #parameters for the refocusing on the particles
    exp.dims = [1,1,1.5]
    exp.accuracy = [0.1,0.1,0.1]

    # How much time between refocusing
    exp.time_for_refocusing = 5*60 # In seconds

    # Saving the files
    name = 'spectra_initial'

    savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    # Not overwrite
    i=1
    filename = '%s_%s.dat'%(name,i)
    while os.path.exists(savedir+filename) or os.path.exists(savedir+filename+'.temp'):
        i += 1
        filename = '%s_%s.dat' %(name,i)
    print('Data will be saved in %s'%(savedir+filename))

    header = 'Time(s),\t Wavelength(nm),\t Central_wavelength(nm),\t Temperature(V),\t Description,\t \
        Pcle,\t Power(uW),\t Counts,\t X(um),\t Y(um),\t Z(um)'

    ## Making header.
    fl = open(savedir+filename+'.temp','a') # Appends to previous files
    fl.write(header)
    fl.write('\n')
    fl.flush()
    ##
    t_0 = time.time() # Initial time
    acquire_spectra = True

    input('Press enter when WhiteLight is on and everything is ready')
    while acquire_spectra:
        print('Aquiring WhiteLight data...')
        temp = exp.adw.adc(exp.temp,2)
        print('Starting with temperature %s'%temp)

        #exp.pmeter.wavelength = 532

        for k in range(len(particles)):
            print('-> Particle %s out of %s'%(k+1,len(particles)))
            how = {'type':'fixed',
                    'device':None,
                    'values': 0,
                    'description': 'White light'}

            particles[k] = exp.acquire_spectra(particles[k],how,spec_wl)
            while exp.spec.remaining_data>0:
                fl.write(exp.spec.get_data())
                fl.write('\n')
                fl.flush()
        print('##############################################')
        print('-> Time for backgrounds...')
        bkg_center = background.get_center()
        bkg_center[2] = particles[-1].get_center()[2] # Gets the Z position of the last particle
        background.set_center(bkg_center)
        exp.acquire_spectra(background,how,spec_wl)
        while exp.spec.remaining_data>0:
            fl.write(exp.spec.get_data())
            fl.write('\n')
            fl.flush()
        print('Done...')
        acquire_spectra = False


    while exp.spec.remaining_data>0:
        fl.write(exp.spec.get_data())
        fl.write('\n')

    fl.flush()
    fl.close()
    fl = open(savedir+filename,'wb') # Erases any previous content
    pickle.dump(exp.spec,fl)
    fl.close()
    print('Saving all the experiment information to %s'%(savedir+filename))
    print('Program finish')
