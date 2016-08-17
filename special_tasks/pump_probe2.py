"""
Pump-probe scan
"""

from datetime import datetime
import os
import os.path
import sys
import time

import numpy as np
from matplotlib import pyplot as plt

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path = [os.path.dirname(os.path.dirname(__file__))] + sys.path

from lib.adq_mod import adq
from lib.config import DeviceConfig
from lib.owis import OWISStage

if __name__ == '__main__':

    print('Connecting to ADwin and loading the external scan code')
    adw = adq()
    adw.load('lib/adbasic/external_scan.T95')

    print('Connecting to the OWIS stage')
    with OWISStage() as owis:
        if not owis.check_if_ready():
            print('STAGE NOT READY. EXITING')
            sys.exit(1)

        try:
            start_str = input('Enter start point [ps]: ')
            start = float(start_str)
            length_str = input('Enter scan length [ps]: ')
            length = float(length_str)
            steps_str = input('Enter number of steps: ')
            steps = int(steps_str)
            t_int_str = input('Enter integration time [ms]: ')
            t_int = 1e-3 * float(t_int_str)
        except ValueError:
            print('ERROR: Invalid input')
            sys.exit(2)

        print('Doing scan!')

        detectors = list(map(DeviceConfig, ('Lock-in X', 'Lock-in Y')))

        with owis.scan(start, length, steps, t_int, adw, detectors, load_adw_program=False) as scan:

            while scan.running():
                sys.stdout.write('\r... {:.1f} ps       '.format(owis.get_position()))
                sys.stdout.flush()
                time.sleep(.2)
            print('\r  DONE                       ')

            data_x, data_y = scan.get_data()

        step = length / steps
        time_axis = np.arange(start, start+length, step)
        data_x_volts = 10 * (data_x - 2**15) / 2**15
        data_y_volts = 10 * (data_y - 2**15) / 2**15

        r2 = data_x**2 + data_y**2
        peakindex = np.argmax(r2)
        peaktime = time_axis[peakindex]
        print('Moving to {} ps'.format(peaktime))
        owis.goto(peaktime)

        now = datetime.now()

        plt.plot(time_axis, data_x_volts)
        
        plt.show()

        datadir = r'd:\data\{date}'.format(date=now.strftime('%Y-%m-%d'))
        if not os.path.exists(datadir):
            os.mkdir(datadir)
        elif not os.path.isdir(datadir):
            sys.stderr.write('ERROR: {} is exists, but is not a directory!\n')
            sys.stderr.write('       Cannot save data.\n')
            sys.stderr.write('       Aborting!\n')
            sys.exit(1)
        fname = datadir + now.strftime(r'\pump_probe_%Y-%m-%d_%H%M.dat')

        header = ('# Pump-probe scan\n' + 
                  '# start {} ps | length {} ps | {:d} steps | {:.0f} ms real time per step\n'
                        .format(start, length, steps, t_int * 1e3) + 
                  'Time [ps]\tLock-In X [V]\tLock-In Y[V]\n')

        dataarray = np.vstack([time_axis, data_x_volts, data_y_volts]).T
        print ('dataarray has shape {}'.format(dataarray.shape))
        np.savetxt(fname, dataarray, delimiter='\t', newline='\n', comments='', header=header)

        print('Saved {}'.format(fname))


