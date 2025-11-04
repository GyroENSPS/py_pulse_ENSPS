from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
import pyvisa
import time

class RF_keysight_generators(QObject):


    def __init__(self, RF1_gpib = 'TCPIP0::169.254.5.21::INSTR', RF2_gpib = 'TCPIP0::169.254.44.127::INSTR'):
        super().__init__()
        self.RF1_device = self.connect_device(RF1_gpib)
        self.RF2_device = self.connect_device(RF2_gpib)

        self.wait_time = 0.1
        self.clock_sync()

    @pyqtSlot(dict)
    def connect_device(self, gpib):
        try :
            rm = pyvisa.ResourceManager('@py')
            keysight1 = rm.open_resource(gpib)
            print("connected to", gpib)

            return keysight1
        except Exception as e:
            print(f"[Error] {e} (could not connect Keysight generators)")
            return

    def clock_sync(self):
        self.RF1_device.write(':ROSC:SOUR INT')
        time.sleep(self.wait_time)
        self.RF2_device.write(':ROSC:SOUR EXT')
        time.sleep(self.wait_time)

    def set_frequency(self,freq):
        freq1_1 = freq["RF1_ch1_freq"]
        freq1_2 = freq["RF1_ch2_freq"]
        freq2_1 = freq["RF2_ch1_freq"]
        freq2_2 = freq["RF2_ch2_freq"]

        self.RF1_device.write('SOURce1:FREQ ' + str(freq1_1))
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce2:FREQ ' + str(freq1_2))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce1:FREQ ' + str(freq2_1))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce2:FREQ ' + str(freq2_2))
        time.sleep(self.wait_time)

        # current_freq = self.RF1_device.query('SOURce1:FREQ?')
        # print(f"RF1_CH1 : {current_freq} Hz")
        # time.sleep(self.wait_time)
        # current_freq = self.RF1_device.query('SOURce2:FREQ?')
        # print(f"RF1_CH2 : {current_freq} Hz")
        # time.sleep(self.wait_time)
        # current_freq = self.RF2_device.query('SOURce1:FREQ?')
        # print(f"RF2_CH1 : {current_freq} Hz")
        # time.sleep(self.wait_time)
        # current_freq = self.RF2_device.query('SOURce2:FREQ?')
        # print(f"RF2_CH2 : {current_freq} Hz")
        # time.sleep(self.wait_time)

    #
    #
    def set_Vpp(self, Vpps):

        Vpp1_1 = Vpps["RF1_ch1_Vpp"]
        Vpp1_2 = Vpps["RF1_ch2_Vpp"]
        Vpp2_1 = Vpps["RF2_ch1_Vpp"]
        Vpp2_2 = Vpps["RF2_ch2_Vpp"]

        self.RF1_device.write('SOURce1:VOLT ' + str(Vpp1_1))
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce2:VOLT ' + str(Vpp1_2))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce1:VOLT ' + str(Vpp2_1))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce2:VOLT ' + str(Vpp2_2))
        time.sleep(self.wait_time)

    def set_phase(self, phases):

        phase_1_1 = phases["RF1_ch1_phase"]
        phase_1_2 = phases["RF1_ch2_phase"]
        phase_2_1 = phases["RF2_ch1_phase"]
        phase_2_2 = phases["RF2_ch2_phase"]

        self.sync_phases()
        self.RF1_device.write('SOURce1:PHASe ' + str(phase_1_1))
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce2:PHASe ' + str(phase_1_2))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce1:PHASe ' + str(phase_2_1))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce2:PHASe ' + str(phase_2_2))

    def sync_phases(self):
        self.RF1_device.write('SOURce1:PHASe: SYNChronize')
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce2:PHASe: SYNChronize')
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce1:PHASe: SYNChronize')
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce2:PHASe: SYNChronize')
        time.sleep(self.wait_time)


    def set_output(self, outputs):

        output_1_1 = outputs["RF1_ch1_output"]
        output_1_2 = outputs["RF1_ch2_output"]
        output_2_1 = outputs["RF2_ch1_output"]
        output_2_2 = outputs["RF2_ch2_output"]

        self.RF1_device.write(':OUTP1 ' + str(output_1_1))
        time.sleep(self.wait_time)
        self.RF1_device.write(':OUTP2 ' + str(output_1_2))
        time.sleep(self.wait_time)
        self.RF2_device.write(':OUTP1 ' + str(output_2_1))
        time.sleep(self.wait_time)
        self.RF2_device.write(':OUTP2 ' + str(output_2_2))

    def set_burst(self, burst):
        burst_1_1 = burst["RF1_ch1_phase"]
        burst_1_2 = burst["RF1_ch2_phase"]
        burst_2_1 = burst["RF2_ch1_phase"]
        burst_2_2 = burst["RF2_ch2_phase"]
        phase_1_1 = burst["RF1_ch1_phase"]
        phase_1_2 = burst["RF1_ch2_phase"]
        phase_2_1 = burst["RF2_ch1_phase"]
        phase_2_2 = burst["RF2_ch2_phase"]

        self.RF1_device.write('SOURce1:BURS:STAT ' + str(burst_1_1))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce1:BURS:STAT ' + str(burst_2_1))
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce1:BURS:MODE GATed')
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce1:BURS:MODE GATed')
        time.sleep(self.wait_time)
        self.RF1_device.write('TRIG:SOUR EXT')
        time.sleep(self.wait_time)
        self.RF2_device.write('TRIG:SOUR EXT')
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce2:BURS:STAT ' + str(burst_1_2))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce2:BURS:STAT ' + str(burst_2_2))
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce2:BURS:MODE GATed')
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce2:BURS:MODE GATed')
        time.sleep(self.wait_time)
        self.RF1_device.write('TRIG:SOUR EXT')
        time.sleep(self.wait_time)
        self.RF2_device.write('TRIG:SOUR EXT')
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce1:BURS:PHAS ' + str(phase_1_1))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce1:BURS:PHAS ' + str(phase_2_1))
        time.sleep(self.wait_time)
        self.RF1_device.write('SOURce2:BURS:PHAS ' + str(phase_1_2))
        time.sleep(self.wait_time)
        self.RF2_device.write('SOURce2:BURS:PHAS ' + str(phase_2_2))



