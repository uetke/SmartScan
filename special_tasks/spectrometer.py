# -*- coding: utf-8 -*-
"""
    Collection of functions useful for controlling the Acton 500i spectrometer through the ADwin box.
    It also includes a class for connected with the remote computer using sockets
"""
import sys
import os
from numpy import savetxt
from time import sleep
import socket
import pickle

def abort(savedir,name,data,header):
    """ In case of aborting saves data variable to file. With the specified header.
    The function checks if the file already exists to avoid overwriting to it.
    """

    # Checks trailing / in savedir
    if savedir[-1] != '/' or savedir[-1] != '\\':
        savedir += '\\'

    # Checks whether the specified name exists in the given directory
    i = 0
    filename = '%s_abort.dat'%(name)
    while os.path.exists(savedir+filename):
        i += 1
        filename = '%s_%s_abort.dat' %(name,i)

    savetxt("%s%s_abort.dat" %(savedir,filename), data,fmt='%s', delimiter=",", header=header)
    print("Aborting execution. Data file saved in %s%s_abort.dat"%(savedir,filename))
    sys.exit(0)

def trigger_spectrometer(adw,digin=1,digout=0,digcheck=2):
    """ Function for triggering the spectrometer and waiting until it finishes acquiring.
        Variables:
        adq - class for the ADwin box
        digin - digital port where the output of the spectrometer is connected
        digout - digital port where the input of the spectrometer is connected
        digcheck - digital port where digout is connected (to check the change of status after triggering)
        REMINDER:
                Connect digin to SCAN
                Connect digout to External Sync
    """

    adw.set_digout(digout)   # This triggers the spectrometer if it is set to +edge (as it should be!)
    sleep(0.1)
    while adw.get_digin(digin) or adw.get_digin(digcheck):
        sleep(0.1)
        adw.clear_digout(0) # Tries to clear the digout every time until the acquisition of the spectra is done
    sleep(0.1) # Gives enough time to the spectrometer to re arm itself.
    if adw.get_digin(digcheck) == 1:
            raise Exception('Not Clearing digout')

class client_spectrometer():
    def __init__(self):
        self.host = socket.gethostname()
        self.port = 12345                   # The same port as used by the server
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def goto(self,wl):
        """ Sends the command for the spectrometer to go to a particular central
            wavelength.
        """"
        self.s.connect((host, port))
        msg = {'type': 'move','value':float(wl)}
        msg = pickle.dumps(msg)
        self.s.sendall(msg) # Message may be broken if the network is not stable

        data = self.s.recv(8192)
        try:
            out = pickle.loads(data)
            self.s.close()
        except:
            self.s.close()
            raise Exception('Spectrometer didn\'t change position')

        return float(out)
