# Collection of functions for acquiring spectra of Particles
from spectrometer import abort, trigger_spectrometer

def acquire_sequence(coordinates,digin=1,digout=0,digcheck=2):
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
            trigger_spectrometer(adw)
            print('Done with particle %i of %i'%(i+1,num_particles))
        print('Particles spectra taken')