# Collection of functions for acquiring spectra of Particles


def acquire_sequence(coordinates,ports):
    """ Function for acquiring a series of spectra of the given particles. 
        
        Args: 
            coordinates (array): 3xN array of coordinates of the particles on which to take spectra
            ports (array): ports where the spectrometer is connected. The first component should be the output port, the second the input port.
        """
    for i in range(num_particles):
            center = data[i,1:4].astype('float')
            center[2] = zcenter
            adw.go_to_position(devs,center)
            #data[i,1:4] = adw.focus_full(counter,devs,center,dims,accuracy,rate=1,speed=50)
            time.sleep(0.5) 
            adw.set_digout(0)           
            time.sleep(0.5)    
            adw.clear_digout(0)
            while adw.get_digin(1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 113: #113 is ascii for letter q
                         abort(filename+'_init')
                time.sleep(0.1)
            print('Done with particle %i of %i'%(i+1,num_particles))
        print('532nm particle spectra taken')