"""
    keep_track_plot.py
    -------------
    Plots the results of keep_track.py
    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl

"""

import matplotlib.pyplot as plt
import numpy as np

today = 'D:\\Data\\2015-07-17\\'

if __name__ == '__main__':
    name = 'spectra_temperature_keep_track_1.dat.temp'
    file = today+name
    data = np.loadtxt(file,dtype='bytes',delimiter =',').astype('str')
    f1 = plt.figure()
    plt.plot(data[1:,0],data[1:,1],'o')
    plt.plot(data[1:,0],data[1:,2],'o')
    plt.plot(data[1:,0],data[1:,3],'o')
    plt.xlabel('Time (s)')
    plt.ylabel('Position (\mu m)')
    plt.figure()
    plt.plot(data[1:,0],data[1:,6],'o')
    plt.show()