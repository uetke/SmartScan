"""
    keep_track_plot.py
    -------------
    Plots the results of keep_track.py
    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl

"""

import matplotlib.pyplot as plt
import numpy as np

today = 'D:\\Data\\2015-05-11\\'

if __name__ == '__main__':
    name = 'tracking__2.dat'
    file = today+name
    data = np.loadtxt(file,dtype='bytes',delimiter =',').astype('str')
    plt.plot(data[2:,0],data[2:,1])
    plt.plot(data[2:,0],data[2:,2])
    plt.plot(data[2:,0],data[2:,3])
    plt.plot(data[2:,0],data[2:,6])
    plt.show()