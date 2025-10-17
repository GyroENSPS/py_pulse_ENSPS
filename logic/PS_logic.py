from idlelib.run import Executive

from PIL.JpegImagePlugin import samplings
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
import time
import numpy as np
from pulsestreamer import PulseStreamer, Sequence, ClockSource


from copy import copy

class Pattern:

    def __init__(self):
        self.p = {}

    def set_digital(self, channel: int, pattern: list):
        self.p[channel] = pattern

    def set_analog(self, channel: int, pattern: list):
        self.p[channel] = pattern

    def get_length(self, channel: int = -1):
        if channel>=0:
            return np.sum(self.p[channel], axis=0)[0]
        m = 0
        for c in self.get_channels():
            length = self.get_length(c)
            m = length if length > m else m
        return m

    def get_channels(self):
        return self.p.keys()

    def equalize(self):
        length = self.get_length()
        for c in self.get_channels():
            l = self.get_length(c)
            if length == l:
                continue
            else:
                rest = length - l
                self.p[c] = self.p[c] + [(rest, 0)]

    def repeat(self, num: int):
        self.equalize()
        for c in self.get_channels():
            self.p[c] = self.p[c] * num
        return self

    def append(self, pattern: 'Pattern'):
        self.equalize()
        pattern.equalize()
        length = self.get_length()
        # test if every channel in pattern
        for c in pattern.get_channels():
            if c not in self.get_channels():
                self.p[c]=[(length, 0)]
        for c in self.get_channels():
            if c in pattern.get_channels():
                self.p[c] = self.p[c]+pattern.p[c]
            else:
                continue
        return self

# === Background worker class (simulating acquisition) ===
class PS(QObject):
    PS_streaming = pyqtSignal()
    finished = pyqtSignal()
    def __init__(self, device_id="169.254.8.2", channel=0, device_ip = "192.168.148.98"):
        super().__init__()
        self.PS_device_id = device_id
        self._running = True
        self.PS_instance = PulseStreamer(self.PS_device_id)

    @pyqtSlot()
    def select_clock(self):
        self.PS_instance.selectClock(ClockSource.EXT_10MHZ)

    def load_pattern(self, pattern_tuples):
        for i in range(len(pattern_tuples)):
            print("patter tupples", np.shape(pattern_tuples[i]))
        pattern_digital = Pattern()
        pattern_analog = Pattern()
        try:
            for i in range(8):
                pattern_digital.set_digital(i, pattern_tuples[i])

            for i in [8,9]:
                pattern_analog.set_analog(i-8, pattern_tuples[i])

            pattern_pp = self.PS_instance.createSequence()

            for channel in pattern_digital.get_channels():
                pattern_pp.setDigital(channel, pattern_digital.p[channel])

            for channel in pattern_analog.get_channels():
                pattern_pp.setAnalog(channel, pattern_analog.p[channel])

            print("Pulse sequence pattern ready")
            return pattern_pp
        except Exception as e:
            print(f"[load pattern Error] {e}")
            pass


    def run_continuous(self, pattern_pp):
        n_runs = PulseStreamer.REPEAT_INFINITELY
        print("pattern : ", pattern_pp)
        self.PS_instance.stream(pattern_pp, n_runs)
        self.PS_streaming.emit()




    def stop_streaming(self):
        self.PS_instance.reset()
        self.finished.emit()





