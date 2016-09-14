"""
Pump-probe scan series
"""

from datetime import datetime
import os
import os.path
import sys
import time
# Because Windows is a frightful steaming piece of useless crap with the
# sorriest excuse for a POSIX layer you've ever seen, the select module
# which any reasonable person would use to check for keypresses is
# completely crippled. Thus, a Windows-only solution is used.
# (As this is actually only used on Windows this has not been made
# portable)
import msvcrt

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from PyQt4.QtCore import QThread, pyqtSignal
from PyQt4.QtGui import QApplication, QMainWindow, QVBoxLayout

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path = [os.path.dirname(os.path.dirname(__file__))] + sys.path

from devices.DriverSR844 import SR844Serial
from lib.adq_mod import adq
from lib.config import DeviceConfig, VARIABLES
from lib.owis import OWISStage
from GUI.serial_helper.powermeter import PowerMeterWindow

def main():
    print('\n####################################################################\n')
    print('Connecting to ADwin and loading the external scan code')
    adw = adq()
    adw.load('lib/adbasic/external_scan.T95')

    owis = OWISStage()
    lockin_config = DeviceConfig('Lock-In', 'Serial')
    lockin_port = lockin_config['Hardware']['PortID']
    lockin = SR844Serial(lockin_port)

    try:
        print('Connecting to the OWIS stage')
        owis.connect()

        if not owis.check_if_ready():
            print('STAGE NOT READY. EXITING')
            return 1

        print('Connecting to to the Lock-In amplifier on {}'.format(lockin_port))
        lockin.initialize()

        lockin_range_uV = lockin.sensitivity.to('µV').m

        print('Lock-In range is {} µV\n'.format(lockin_range_uV))

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
            return 2

        # Sadly we can't get the particle position from ADwin right now...
        try:
            x_str = input('x position [µm]: ')
            x = float(x_str)
            y_str = input('y position [µm]: ')
            y = float(y_str)
            z_str = input('z position [µm]: ')
            z = float(z_str)
            stay_put_str = input('are we in the right place [Y/n]? ')
            stay_put = len(stay_put_str.strip()) == 0 or stay_put_str[0].lower() in ('y', 'j', '1')
        except ValueError:
            print('ERROR: Invalid input')
            return 2
        

        default_datadir = r'd:\data\{date}'.format(date=datetime.now().strftime('%Y-%m-%d'))
        datadir = input('Directory to save data [{}]: '.format(default_datadir))
        datadir = datadir.strip()
        if not datadir:
            datadir = default_datadir

        if not os.path.exists(datadir):
            os.mkdir(datadir)
        elif not os.path.isdir(datadir):
            sys.stderr.write('ERROR: {} exists, but is not a directory!\n')
            sys.stderr.write('       Cannot save data.\n')
            sys.stderr.write('       Aborting!\n')
            return 1


        if not stay_put:
            print("Moving the piezo stage into position")

            xyzpiezo = list(map(DeviceConfig, ('x piezo', 'y piezo', 'z piezo')))

            adw.go_to_position(xyzpiezo, (x,y,z))


        gui_app = QApplication([sys.argv[0]])

        print('Constructing a shell of a figure')
        figure_window = MplWindow(start, length)
        figure_window.show()

        print('Starting the power meter app')
        powermeter_window = PowerMeterWindow(figure_window)
        powermeter_window.show()

        print('Connecting to the power meter')
        powermeter_window.do_connect()
        powermeter = powermeter_window._pm

        print('Starting the main script')
        worker = PumpProbeSeriesThread(adw, owis, lockin, powermeter_window, figure_window,
                                       (x,y,z), start, length, steps, t_int, datadir)

        worker.start()

        return gui_app.exec_()

    finally:
        print('Disconnecting from devices')
        owis.close()
        lockin.finalize()

    return 0


def wait_for_buttonpress(adw, btns, keys=[], *, accept_keyboard=True):
    """
    Wait for user input, either by button (connected to adw) or by keyboard.

    btns is a sequence of integers that are acceptable button numbers.
    keys is a sequence of keys that are acceptable as keyboard input, but should
    NOT be polled for button presses (because there's no button connected)

    NOTE: Button numbers are 1-indexed *here*; adwin digital inputs 0-indexed
    """
    if isinstance(btns, int):
        btns = [btns]
    btns_bytes = [str(b).encode('ISO-8859-15') for b in btns]
    keys_bytes = [str(b).encode('ISO-8859-15') for b in keys]
    while True:
        c = None
        if accept_keyboard and msvcrt.kbhit():
            c = msvcrt.getch()
            if c in btns_bytes or c in keys_bytes:
                return int(c) if c.isdigit() else c
            else:
                print('Unrecognized: {}'.format(repr(c)))
                #msvcrt.ungetch(c)

        for btn in btns:
            # 
            if adw.get_digin(btn-1) == 0:
                # Wait for the button release event
                while adw.get_digin(btn-1) == 0:
                    time.sleep(0.01)
                return btn
        time.sleep(0.02)


class MplWindow(QMainWindow):
    updated = pyqtSignal()

    def __init__(self, start, length, parent=None):
        super().__init__(parent)

        self._start = start
        self._length = length

        self.figure = plt.figure()
        self.axes1 = self.figure.add_subplot(211)
        self.axes2 = self.figure.add_subplot(212)

        self.canvas = FigureCanvas(self.figure)

        self.setCentralWidget(self.canvas)

        self.updated.connect(self.canvas.draw)

    def setup_figure_xy(self):
        self.axes1.set_xlabel('Pulse delay (ps)')
        self.axes1.set_xlim(self._start, self._start+self._length)
        self.axes1.set_ylabel('Lock-In X (µV)')

        self.axes2.set_xlabel('Pulse delay (ps)')
        self.axes2.set_xlim(self._start, self._start+self._length)
        self.axes2.set_ylabel('Lock-In Y (µV)')

    def setup_figure_Rtheta(self, start, stop):
        self.axes1.set_xlabel('Pulse delay (ps)')
        self.axes1.set_xlim(start, stop)
        self.axes1.set_ylabel('Lock-In R (µV)')

        self.axes2.set_xlabel('Pulse delay (ps)')
        self.axes2.set_xlim(start, stop)
        self.axes2.set_ylabel('Lock-In θ (µV)')



class PumpProbeSeriesThread(QThread):
    def __init__(self, adq, owis, lockin, pmwin, figwin, xyz, start, length, steps, t_int, datadir):
        super().__init__()

        self._adw = adq
        self._owis = owis
        self._lockin = lockin
        self._pm_window = pmwin
        self._powermeter = pmwin._pm
        self._figwin = figwin
        self._xyz = xyz
        self._start = start
        self._length = length
        self._steps = steps
        self._t_int = t_int
        self._datadir = datadir
        self._maxtime = None
        self._autorefocus = True
        self._quit = False

        self.heating_power = 0

        self._plot1 = None
        self._plot2 = None

    def run(self):
        print('PRESS BUTTON 1 TO CONTINUE')
        wait_for_buttonpress(self._adw, 1, accept_keyboard=False)
        print('PRESS BUTTON 2 TO CONTINUE')
        wait_for_buttonpress(self._adw, 2, accept_keyboard=False)
        print('ok.\n')

        while not self._quit:
            self.handle_input()

    def find_peak(self):
        print('Please unblock the pump-probe beam!')
        print('Press any key to continue.\n')
        msvcrt.getch()

        print('Finding the pump-probe peak')
        start1 = self._start
        length1 = 100
        steps1 = 500
        step1 = 0.20
        t_int1 = 10e-3

        time_axis = np.arange(start1, start1+length1, step1)

        # Detect R
        detectors = list(map(DeviceConfig, ('Lock-in X', 'Lock-in Y')))
        self._lockin.front_output[1] = 'Display'
        self._lockin.front_output[2] = 'Display'
        self._lockin.display[1] = 'Rv'
        self._lockin.display[2] = 'Theta'

        with self._owis.scan(start1, length1, steps1, t_int1,
                             self._adw, detectors, load_adw_program=False) as scan:
            self._figwin.setup_figure_Rtheta(start1, start1+length1)

            while scan.running():
                self.plot_data(time_axis, *self.data_in_µV(scan))
                time.sleep(0.5)
                sys.stdout.write('.')
                sys.stdout.flush()

            self.plot_data(time_axis, *self.data_in_µV(scan))

        maxidx = np.argmax(self.data_x_µV)
        maxtime = start1 + maxidx * step1
        print('Maximum is at {}.'.format(maxtime))
        self._maxtime = maxtime

    def handle_input(self):
        print('Setting power meter to 532nm')
        self._powermeter.set_wavelength(532)

        print('Auto-refocus is {}'.format(['OFF', 'ON'][self._autorefocus]))

        print('Press a button or key:')
        print('(1) Measure 532nm power')
        print('(2) Do pump probe scan')
        print('(3) Refocus')
        print('(4) Move delay line to position')
        print('(5) Go to peak')
        print('(6) Find peak')
        print('(7) Enter new (xyz) location')
        if self._autorefocus:
            print('(8) Disable auto-refocus')
        else:
            print('(8) Enable auto-refocus')
        print('(q) Quit')

        button = wait_for_buttonpress(self._adw, [1, 2], [1, 2, 3, 4, 5, 6, 7, 8, 'q'])
        if button == 1:
            self.measure_power()
        elif button == 2:
            self.measure_pump_probe()
        elif button == 3:
            print('Refocus')
            print('Please unblock the pump-probe beam!')
            print('Press any key to continue.\n')
            msvcrt.getch()
            self.refocus()
        elif button == 4:
            print('Current position:', self._owis.get_position())
            try:
                new_pos_str = input('New position: ')
                new_pos = float(new_pos_str)
            except ValueError:
                print('Error parsing number.\n')
            else:
                self._owis.goto(new_pos)
                time.sleep(1)
                while not self._owis.check_if_ready():
                    time.sleep(1)
                    sys.stdout.write('.')
                    sys.stdout.flush()
                print('\nCurrent position:', self._owis.get_position())
        elif button == 5:
            if self._maxtime is None:
                self.find_peak()
            print('Moving to peak')
            self._owis._stage.abort()
            self._owis.goto(self._maxtime)
            time.sleep(1)
            while not self._owis.check_if_ready():
                time.sleep(1)
            print('Current position:', self._owis.get_position())
        elif button == 6:
            self.find_peak()
        elif button == 7:
            try:
                x_str = input('x position [µm]: ')
                x = float(x_str)
                y_str = input('y position [µm]: ')
                y = float(y_str)
                z_str = input('z position [µm]: ')
                z = float(z_str)
                stay_put_str = input('are we in the right place [Y/n]? ')
                stay_put = len(stay_put_str.strip()) == 0 or stay_put_str[0].lower() in ('y', 'j', '1')
            except ValueError:
                print('Invalid input!')
                return

            self._xyz = x, y, z

            if not stay_put:
                print("Moving the piezo stage into position")

                xyzpiezo = list(map(DeviceConfig, ('x piezo', 'y piezo', 'z piezo')))

                self._adw.go_to_position(xyzpiezo, (x,y,z))
        elif button == 8:
            self._autorefocus = not self._autorefocus
        elif button == 'q':
            self._quit = True
        else:
            raise ValueError('Impossible button event!')


    def measure_power(self):
        print('Block the pump-probe beam and confirm when ready (btn 1)')
        wait_for_buttonpress(self._adw, 1)
        power_µW = self._powermeter.power * 1e6
        self.heating_power = power_µW
        print('Heating power is {} µW\n'.format(power_µW))

    def measure_pump_probe(self):
        print('Unblock the pump-probe beam and confirm when ready (btn 2)')
        wait_for_buttonpress(self._adw, 2)
        print('ok.')

        if self._autorefocus:
            print('Auto refocus!')
            self.refocus()

        print('Setting the lock-in outputs')
        self._lockin.front_output[1] = 'X'
        self._lockin.front_output[2] = 'Y'

        step = self._length / self._steps
        time_axis = np.arange(self._start, self._start+self._length, step)

        detectors = list(map(DeviceConfig, ('Lock-in X', 'Lock-in Y')))

        now = datetime.now()

        print('Hold button 1 to abort')

        with self._owis.scan(self._start, self._length, self._steps, self._t_int,
                             self._adw, detectors, load_adw_program=False) as scan:

            self._figwin.setup_figure_xy()


            while scan.running():
                self.plot_data(time_axis, *self.data_in_µV(scan))
                time.sleep(0.5)
                sys.stdout.write('.')
                sys.stdout.flush()

                if self._adw.get_digin(0) == 0:
                    print('ABORTING')
                    self._owis._stage.abort()
                    scan.cancel()
                    self.data_in_µV(scan)
                    time.sleep(1)
                    print('!\n')
                    #wait_for_buttonpress(self._adw, 0)
                    return

            self.plot_data(time_axis, *self.data_in_µV(scan))
            print('\nDONE\n')

        # r2 = self.data_x_µV**2 + self.data_y_µV**2
        # peakindex = np.argmax(r2)
        # peaktime = time_axis[peakindex]
        # print('Moving to {} ps'.format(peaktime))
        # self._owis.goto(peaktime)

        fname = os.path.join(self._datadir, now.strftime(r'pump_probe_%Y-%m-%d_%H%M.dat'))

        header = ('Pump-probe scan\n' + 
                  'start {} ps | length {} ps | {:d} steps | {:.0f} ms real time per step\n'
                        .format(self._start, self._length, self._steps, self._t_int * 1e3) + 
                  'Lock-In range {} µV\n'.format(self._lockin.sensitivity.to('µV').m) +
                  'Heating {} µW\n\n'.format(self.heating_power) +
                  'Time [ps]\tLock-In X [µV]\tLock-In Y [µV]\n')

        dataarray = np.vstack([time_axis, self.data_x_µV, self.data_y_µV]).T

        np.savetxt(fname, dataarray, delimiter='\t', newline='\n', comments='', header=header)
        print('Saved {}\n'.format(fname))



    def data_in_µV(self, scan):
        data_x, data_y = scan.get_data()

        lockin_range_uV = self._lockin.sensitivity.to('µV').m

        self.data_x_µV = lockin_range_uV * (data_x - 2**15) / 2**15
        self.data_y_µV = lockin_range_uV * (data_y - 2**15) / 2**15

        return self.data_x_µV, self.data_y_µV

    def plot_data(self, time_axis, data_x_µV, data_y_µV):
        if self._plot1 is not None:
            self._figwin.axes1.lines.remove(self._plot1[0])
            self._figwin.axes2.lines.remove(self._plot2[0])

        self._plot1 = self._figwin.axes1.plot(time_axis, data_x_µV, 'k-')
        self._plot2 = self._figwin.axes2.plot(time_axis, data_y_µV, 'k-')
        
        self._figwin.axes1.set_ylim(-0.01, +0.01)
        self._figwin.axes2.set_ylim(-0.01, +0.01)
        self._figwin.axes1.relim()
        self._figwin.axes2.relim()
        self._figwin.axes1.autoscale(True, 'y')
        self._figwin.axes2.autoscale(True, 'y')

        self._figwin.updated.emit()

    def refocus(self):
        self._owis._stage.abort()
        if self._maxtime is None:
                self.find_peak()
        self._owis.goto(self._maxtime)
        time.sleep(1)
        while not self._owis.check_if_ready():
            time.sleep(1)

        xyzpiezo = list(map(DeviceConfig, ('x piezo', 'y piezo', 'z piezo')))

        self._lockin.front_output[1] = 'Display'
        self._lockin.front_output[2] = 'Display'
        self._lockin.display[1] = 'Rv'
        self._lockin.display[2] = 'Theta'

        detector = DeviceConfig('Lock-in X')
        xyz_new = self._adw.focus_full(detector, xyzpiezo, self._xyz, [1,1,1], [0.05, 0.05, 0.05])

        if len(xyz_new) == 3:
            self._xyz = xyz_new
            self._adw.go_to_position(xyzpiezo, xyz_new)
            
            print ('new center:', xyz_new)


if __name__ == '__main__':
    sys.exit(main())
