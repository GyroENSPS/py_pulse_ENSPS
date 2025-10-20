from asyncio import timeout

from PIL.JpegImagePlugin import samplings
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
import time
import numpy as np



import zhinst.core

from hardware_config.MFLI_config.MFLI_setups import *


# === Background worker class (simulating acquisition) ===
class DAQ_MFLI(QObject):
    DAQ_data_ready = pyqtSignal(tuple)   # Signal to send DAQ data to the GUI
    live_data_ready = pyqtSignal(tuple)  # Signal to send live data to the GUI
    finished = pyqtSignal()

    def __init__(self, device_id="dev30496", channel=0, device_ip = "192.168.148.98"):
        super().__init__()
        self.device_id = device_id
        self.channel = channel
        self._running = True
        self.DAQ_data_plot_flag = True

        self.session = zhinst.core.ziDAQServer(device_ip, 8004, 6)  # 6 = API Level

        self.node_path = f"/{device_id}/demods/{channel}/sample"

        # Souscrire au flux
        self.session.subscribe(self.node_path)
        self.session.sync()

        self.clockbase = self.session.getInt(f"/{device_id}/clockbase")

    @pyqtSlot(dict)
    def set_parameters(self, params):
        print(f"Paramètres mis à jour : {params}")

        phase = params["phase"]
        filter_freq = params["filter_freq"]
        n_average = params["n_average"]
        n_points = params["n_points"]
        min_time = params["min_time"]
        max_time = params["max_time"]

        self.session = setup_MFLI_daq_session(self.session, phase=phase,
                                              filter_tau=np.sqrt(2 ** (1 / 8) - 1) / (2 * np.pi * filter_freq))
        self.daq_module = setup_MFLI_daq_module(self.session, phase=phase,
                                                filter_tau=np.sqrt(2 ** (1 / 8) - 1) / (2 * np.pi * filter_freq),
                                                repetitions=n_average, number_of_points=n_points)

        self.run_triggered(min_time, max_time)



    @pyqtSlot()
    def run_triggered(self, min_time, max_time):

        # self.daq_module = setup_lia_for_pulsed_measurements(self.session,edge=2, phase=0, repetitions=1, num_repeat=1, number_of_points=100, cyc_time = 1/130)


        print("daq module configured")

        while self._running:

            duration = 0.00001
            timeout = int(1000 * duration)
            self.daq_module.subscribe('/dev30496/demods/0/sample.X.avg')
            self.daq_module.execute()
            # print("waiting for trigger")
            while self._running and not self.daq_module.finished():
                try:
                    data = self.session.poll(duration, timeout, flags=0)
                    # sample = self.session.getSample(f"/{self.device_id}/demods/{self.channel}/sample")
                    # print(data)
                    samples = data[self.device_id]["demods"][str(self.channel)]["sample"]["x"]
                    timestamps = data[self.device_id]["demods"][str(self.channel)]["sample"]["timestamp"]
                    timestamps = timestamps/self.clockbase
                    # print(samples)
                    # sampling_rate = 1
                    self.live_data_ready.emit((samples, timestamps))
                    # time.sleep(0.01)  # ~100 Hz update rate
                except Exception as e:
                    print(f"[Error] {e}")
                    break
                time.sleep(0.01)

            try :
                result = self.daq_module.read()
                demod_x = result['dev30496']['demods']['0']['sample.x.avg'][0]['value'][0]
                samples = demod_x
                # print(samples)
                time_scale = np.linspace(min_time, max_time*1e-9, len(samples))
                self.DAQ_data_ready.emit((samples, time_scale))
                # print("data acquired")
                # self._running = False
            except:
                print("no data acquired")
                break

        self.finished.emit()

    def run_continuous_dummy(self):
        print("[DAQ] Running in thread:", QThread.currentThread())
        # self.session = setup_MFLI_daq_session(self.session, phase = phase, filter_tau= np.sqrt(2**(1/8) - 1) / (2 * np.pi * filter_freq))

        """This method runs in the background thread."""
        t = [0]
        # Dummy value for testing
        while self._running:
            time.sleep(0.02)  # Simuler un échantillonnage à 50 Hz
            value = [np.sin(2 * np.pi * 0.5 * t[0]) + np.random.normal(0, 0.1)]

            self.live_data_ready.emit((value, t))
            t[0]+=0.02

    def run_continuous(self, phase, filter_freq):
        print("[DAQ] Running in thread:", QThread.currentThread())
        # self.session = setup_MFLI_daq_session(self.session, phase = phase, filter_tau= np.sqrt(2**(1/8) - 1) / (2 * np.pi * filter_freq))

        # """This method runs in the background thread."""
        # t = [0]
        # # Dummy value for testing
        # while self._running:
        #     time.sleep(0.02)  # Simuler un échantillonnage à 50 Hz
        #     value = [np.sin(2 * np.pi * 0.5 * t[0]) + np.random.normal(0, 0.1)]
        #
        #     self.live_data_ready.emit((value, t))
        #     t[0]+=0.02
        duration = 0.1
        timeout = int(1000 * duration)
        while self._running:
            try:
                data = self.session.poll(duration, timeout, flags=0)
                # sample = self.session.getSample(f"/{self.device_id}/demods/{self.channel}/sample")
                # print(data)
                samples = data[self.device_id]["demods"][str(self.channel)]["sample"]["x"]
                timestamps = data[self.device_id]["demods"][str(self.channel)]["sample"]["timestamp"]
                timestamps = timestamps / self.clockbase
                # print(samples)
                # sampling_rate = 1
                self.live_data_ready.emit((samples, timestamps))
                print("live data sent to main thread")
                # time.sleep(0.01)  # ~100 Hz update rate
            except Exception as e:
                print(f"[Error] {e}")
                break
            time.sleep(0.01)
        self.finished.emit()

    def stop(self):
        """Gracefully stop the acquisition loop."""
        self._running = False

