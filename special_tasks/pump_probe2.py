"""
Pump-probe scan
"""

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

        plt.plot(time_axis, data_x)
        plt.show()
