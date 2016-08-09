"""
Pump-probe scan
"""
import concurrent.futures
import os.path
import sys
import time

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path = [os.path.dirname(os.path.dirname(__file__))] + sys.path

from lantz import Q_
import numpy as np

from devices import owis_stage
from lib.adq_mod import adq
from lib.config import DeviceConfig, VARIABLES


def do_pp_scan(stage, axis, start_mm, length_mm, steps, int_time_s, adq, detectors):
    # We want to revert to the old speed of the stage later
    old_speed = stage.speed[axis]

    # Send the stage to its start position
    stage.move_absolute_async(axis, Q_(start_mm, 'mm'))
    sys.stdout.write('moving to start position...')
    sys.stdout.flush()

    length = Q_(length_mm, 'mm')
    trig_dist = length / steps
    total_time = steps * Q_(int_time_s, 's')
    speed = length / total_time

    if speed >= stage.max_speed(axis):
        raise ValueError('Scan too fast! Max stage speed is {}, calculated speed {}'
            .format(stage.max_speed(axis), speed))

    # configure the trigger (while the stage is moving)
    stage.trigger_axis = axis
    stage.trigger_mode = 1
    stage.trigger_signal_length = Q_(5, 'µs')
    stage.trigger_distance = trig_dist

    # tell ADwin which detectors to pick up
    dev_params = np.zeros(len(detectors) * 2, dtype=np.int32)
    for idx, detector in enumerate(detectors):
        dev_params[2*idx] = int(detector['Type'][:5], 36) # What the actual fuck, Aqui...
        dev_params[2*idx+1] = detector['Input']['Hardware']['PortID']
    adq.set_datalong(dev_params, VARIABLES['data']['dev_params'])
    adq.set_par(VARIABLES['par']['Num_devs'], len(detectors))
    adq.set_par(VARIABLES['par']['Scan_length'], steps)

    # wait for the stage to come to rest
    while stage.axis_status[axis] == owis_stage.AxisStatus.moving:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write('\n')
    if stage.axis_status[axis] != owis_stage.AxisStatus.ready:
        raise RuntimeError("Axis status: {}".format(stage.axis_status[axis]))

    # Start everything up!
    adq.start(5)
    stage.speed[axis] = speed
    stage.trigger_enabled = True
    stage.move_relative_async('X', length)

    # And now we wait!
    while 1:
        ax_status = stage.axis_status[axis]
        moving = (ax_status == owis_stage.AxisStatus.moving)
        running = adq.adw.Process_Status(5)
        n_px = adq.get_par(VARIABLES['par']['Pix_done'])
        pos = stage.position[axis]

        sys.stdout.write('\r{} - {:.1f} mm - process status {} - {} px done   '.format(
            ax_status.human_readable_name(), pos.to('mm').m, running, n_px))
        sys.stdout.flush()

        if moving or running:
            time.sleep(0.1)
        else:
            break
    print()
    data = adq.get_fifo(VARIABLES['fifo']['Scan_data'])
    print('Dataset length: {}'.format(len(data)))

    stage.trigger_enabled = True
    stage.speed[axis] = old_speed


if __name__ == '__main__':
    print('Connecting to ADwin and loading the external scan code')
    adw = adq()
    adw.load('lib/adbasic/external_scan.T95')

    print('Connecting to the OWIS stage')
    owis_cfg = DeviceConfig('IR Delay', 'Serial')
    with owis_stage.LStepStage(owis_cfg['Hardware']['PortID']) as owis:
        print('... connected ({} - SN {})'.format(owis.ver, owis.sn))
        axis = owis_cfg['Hardware']['Axis']
        axis_status = owis.axis_status[axis]
        print('... axis status: {}'.format(axis_status.human_readable_name()))
        if axis_status != owis_stage.AxisStatus.ready:
            print('!!! AXIS NOT READY !!!')
            print('bye.')
            sys.exit(1)
        else:
            owis.velocity_factors = [owis_cfg['Calibration']['VelocityFactor']] * 4
            do_pp_scan(owis, 'X', 10, 100, 600, 3e-2, adw, [DeviceConfig('Lock-in X')])




