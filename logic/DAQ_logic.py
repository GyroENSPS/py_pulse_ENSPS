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
        self.daq_module = setup_lia_for_pulsed_measurements(self.session,edge=2, phase=0, repetitions=1, num_repeat=1, number_of_points=100, cyc_time = 1/130)



    @pyqtSlot()
    def run_triggered(self):
        while self._running:
            duration = 0.1
            timeout = int(1000 * duration)
            self.daq_module.subscribe('/dev30496/demods/0/sample.X.avg')
            self.daq_module.execute()
            while self._running and not self.daq_module.finished():
                try:
                    data = self.session.poll(duration, timeout, flags=0)
                    # sample = self.session.getSample(f"/{self.device_id}/demods/{self.channel}/sample")
                    # print(data)
                    samples = data[self.device_id]["demods"][str(self.channel)]["sample"]["x"]
                    # print(samples)
                    sampling_rate = self.session.getDouble(f"/{self.device_id}/demods/{self.channel}/rate")
                    # sampling_rate = 1
                    self.live_data_ready.emit((samples, sampling_rate))
                    # time.sleep(0.01)  # ~100 Hz update rate
                except Exception as e:
                    print(f"[Error] {e}")
                    break
                time.sleep(0.01)
            result = self.daq_module.read()
            try :
                demod_x = result['dev30496']['demods']['0']['sample.x.avg'][0]['value'][0]
            except:
                break
            samples = demod_x
            time_scale = np.linspace(0, 1300e-6, len(samples))
            self.DAQ_data_ready.emit((samples, time_scale))
        self.finished.emit()


    def run_continuous(self):

        """This method runs in the background thread."""
        t = 0
        # Dummy value for testing
        # while self._running:
        #     time.sleep(0.02)  # Simuler un échantillonnage à 50 Hz
        #     value = np.sin(2 * np.pi * 0.5 * t) + np.random.normal(0, 0.1)
        #     self.DAQ_data_ready.emit(value)
        #     t += 0.02
        duration = 0.1
        timeout = int(1000 * duration)
        while self._running:
            try:
                data = self.session.poll(duration, timeout, flags=0)
                # sample = self.session.getSample(f"/{self.device_id}/demods/{self.channel}/sample")
                # print(data)
                samples = data[self.device_id]["demods"][str(self.channel)]["sample"]["x"]
                # print(samples)
                sampling_rate = self.session.getDouble(f"/{self.device_id}/demods/{self.channel}/rate")
                # sampling_rate = 1
                self.DAQ_data_ready.emit((samples, sampling_rate))
                # time.sleep(0.01)  # ~100 Hz update rate
            except Exception as e:
                print(f"[Error] {e}")
                break
        self.finished.emit()

    def stop(self):
        """Gracefully stop the acquisition loop."""
        self._running = False

