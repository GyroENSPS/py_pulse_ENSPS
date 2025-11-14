import time
import numpy as np

def setup_MFLI_daq_session(daq, phase, filter_tau):
    # Signal Input
    daq.setInt('/dev30496/demods/0/adcselect', 0)
    daq.setInt('/dev30496/sigins/0/imp50', 1)
    daq.setInt('/dev30496/sigins/0/diff', 0)
    daq.setInt('/dev30496/sigins/0/float', 0)
    daq.setInt('/dev30496/sigins/0/ac', 0)
    daq.setDouble('/dev30496/sigins/0/range', 3.00000000)
    daq.setDouble('/dev30496/sigins/0/scaling', 1.00000000)
    # External Reference
    daq.setInt('/dev30496/extrefs/0/enable', 1)
    daq.setInt('/dev30496/demods/1/adcselect', 8)
    daq.setDouble('/dev30496/demods/0/phaseshift', phase)
    daq.setDouble('/dev30496/demods/1/phaseshift', 0)
    daq.setInt('/dev30496/demods/0/harmonic', 1)
    daq.setInt('/dev30496/demods/1/harmonic', 1)
    daq.set('/dev30496/system/extclk', 1)
    # Low-Pass Filter
    # daq.setInt('/dev30496/demods/0/order', 4)
    daq.setInt('/dev30496/demods/0/order', 8)
    daq.setDouble('/dev30496/demods/0/timeconstant', filter_tau)  # filter for 130Hz lock-in freq
    # daq.setDouble('/dev30496/demods/0/timeconstant', 0.015960324595025045)  # filter for 30Hz lock-in freq
    # daq.setDouble('/dev30496/demods/0/timeconstant', 0.00478810) # at 160 Hz
    # daq.set('/dev30496/demods/0/timeconstant', 0.02394049) # at 40Hz

    daq.setInt('/dev30496/demods/0/sinc', 0)
    # Data Transfer
    daq.setInt('/dev30496/demods/0/enable', 1)
    daq.setDouble('/dev30496/demods/0/rate', 3000.00000000)
    daq.setInt('/dev30496/demods/0/trigger', 4)
    # daq.setInt('/dev30496/demods/0/trigger', 128)
    # Output Amplitudes
    daq.setInt('/dev30496/sigouts/0/enables/1', 0)
    # AUX Output 1
    daq.setInt('/dev30496/auxouts/0/outputselect', 0)
    daq.setDouble('/dev30496/auxouts/0/preoffset', 0.00000000)
    # daq.setDouble('/dev30496/auxouts/0/scale', 100000.00000000)
    daq.setDouble('/dev30496/auxouts/0/scale', 100.00000000)
    daq.setDouble('/dev30496/auxouts/0/offset', 0.00000000)
    daq.setDouble('/dev30496/auxouts/0/limitlower', -10.00000000)
    daq.setDouble('/dev30496/auxouts/0/limitupper', 10.00000000)
    return daq


def setup_MFLI_daq_module(daq, phase=190, filter_tau=10 ,  repetitions=1, number_of_points=100):

    # DAQ Module
    daq_module = daq.dataAcquisitionModule()
    daq_module.set('preview', 1)
    daq_module.set('device', 'dev30496')
    daq_module.set('historylength', 100)
    daq_module.set('count', 1)
    daq_module.set('type', 6)
    daq_module.set('edge', 1)
    daq_module.set('bits', 1)
    daq_module.set('bitmask', 1)
    daq_module.set('eventcount/mode', 1)
    daq_module.set('delay', 0.00000000)
    daq_module.set('grid/mode', 4)

    # print('Current time: ', datetime.time(datetime.now()))
    daq_module.set('grid/cols', number_of_points)
    # daq_module.set('duration', num_repeat * number_of_points * cyc_time)
    # print('Time for measuring point (in s): t = ', num_repeat * cyc_time / 1e9)
    # print('Time for a scan (in s): T = ', num_repeat * cyc_time * number_of_points / 1e9)
    # print('Total duration of the measurement (in min): T = ', round(num_repeat * cyc_time * number_of_points * repetitions / 1e9 / 60, 2))

    daq_module.set('bandwidth', 0.00000000)
    daq_module.set('pulse/min', 0.00000000)
    daq_module.set('pulse/max', 0.00100000)
    daq_module.set('holdoff/time', 0.0000000)
    daq_module.set('holdoff/count', 0)
    daq_module.set('grid/rows', 1)
    daq_module.set('grid/repetitions', repetitions)
    daq_module.set('grid/rowrepetition', 1)
    daq_module.set('grid/direction', 0)
    daq_module.set('grid/waterfall', 0)
    daq_module.set('grid/overwrite', 0)
    daq_module.set('fft/window', 1)
    daq_module.set('refreshrate', 5.00000000)
    daq_module.set('awgcontrol', 0)
    daq_module.set('historylength', 100)
    daq_module.set('bandwidth', 0.00000000)
    daq_module.set('hysteresis', 0.01000000)
    daq_module.set('level', 0.10000000)
    daq_module.set('delay', 0.052)
    daq_module.set('triggernode', '/dev30496/demods/0/sample.TrigIn1')
    daq_module.set('save/directory', '/data/LabOne/WebServer')
    daq_module.set('clearhistory', 1)
    return daq_module

def start_lia_daq_module(daq_module, time_conversion=1, max_time = 1, time_offset=0, repeats=100, num_of_points=200, cycle_time=250e3):

    daq_module.subscribe('/dev30496/demods/0/sample.X.avg')
    daq_module.subscribe('/dev30496/demods/0/sample.Y.avg')
    daq_module.subscribe('/dev30496/demods/0/sample.R.avg')
    daq_module.subscribe('/dev30496/demods/0/sample.phase.avg')
    dt = repeats*cycle_time
    daq_module.execute()
    start = time.time()
    while not daq_module.finished():
        time.sleep(dt)
    result = daq_module.read()
    daq_module.unsubscribe('*')
    print('Duration of the measurement (in s): t = ', time.time() - start)
    demod_x = result['dev30496']['demods']['0']['sample.x.avg'][0]['value'][0]
    demod_y = result['dev30496']['demods']['0']['sample.y.avg'][0]['value'][0]
    demod_R = result['dev30496']['demods']['0']['sample.r.avg'][0]['value'][0]
    demod_phase = result['dev30496']['demods']['0']['sample.phase.avg'][0]['value'][0]

    TIME = np.linspace(time_offset, max_time, num_of_points)
    # TIME = TIME/max(TIME)*time_conversion + time_offset
    return TIME, demod_x, demod_y, demod_R, demod_phase