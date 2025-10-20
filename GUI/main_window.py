import pyqtgraph
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QCheckBox, QTableWidgetItem, QComboBox, QAbstractItemView, QDesktopWidget, \
    QApplication, QFileDialog, QInputDialog
from astropy.utils.misc import coffee
#
from GUI.UI_files.table_widget_test import Ui_MainWindow
import configparser
from PyQt5.QtWidgets import QHeaderView
import sys
import os

from dask.array import left_shift

from logic.DAQ_logic import DAQ_MFLI
from logic.pulse_generator_logic import PulseGeneratorLogic
from logic.pulse_table_logic import PulseTableLogic
from logic.var_table_logic import VarTableLogic

import time

import numpy as np
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import QCheckBox, QTableWidgetItem, QComboBox, QMainWindow, QMessageBox, QApplication, QFileDialog
from PyQt5.uic.Compiler.qtproxies import QtWidgets
from mpmath import phase

from GUI.UI_files.table_widget_test import Ui_MainWindow
from GUI.UI_files.PS_config_Window_UI import Ui_PS_config_Form
from GUI.PS_config_window import PS_config_window
from logic.DAQ_logic import DAQ_MFLI
from logic.PS_logic import PS




class MainWindow(PulseTableLogic, VarTableLogic, PulseGeneratorLogic):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # uic.loadUi('GUI/UI_files/table_widget_test.ui', self)
        # self.ui = Ui_MainWindow()

        # Récupérer la géométrie disponible de l'écran
        screen_geometry = QDesktopWidget().availableGeometry()

        # Redimensionner la fenêtre à cette taille
        self.setGeometry(screen_geometry)



        self.show()

        self.showMaximized()
        self.setupUi(self)
        self.channel_colors = [
                                "#1f77b4",  # bleu
                                "#ff7f0e",  # orange
                                "#2ca02c",  # vert
                                "#d62728",  # rouge
                                "#9467bd",  # violet
                                "#8c564b",  # brun
                                "#e377c2",  # rose
                                "#7f7f7f",  # gris
                                "#bcbd22",  # jaune-vert
                                "#17becf"   # cyan
                            ]
        self.list_variable_names = []

        self.pulse_view.setBackground("w")
        self.pulse_view.hideAxis('left')

        self.pulse_sequence_view.setBackground("w")
        self.pulse_sequence_view.hideAxis('left')

        self.tableWidget.setRowCount(11)
        self.tableWidget.setColumnCount(1)

        channels = ["DO0","DO1","DO2","DO3","DO4","DO5","DO6","DO7","AO0","AO1"]
        self.comboBox_trigger_per_sequence_channel.addItems(channels)
        self.comboBox_trigger_per_point_channel.addItems(channels)
        self.comboBox_trigger_per_sequence_channel.setCurrentIndex(9)
        self.comboBox_trigger_per_point_channel.setCurrentIndex(2)



        self.tableWidget.setHorizontalHeaderLabels(["laser"])
        self.tableWidget.setVerticalHeaderLabels(["length","DO0","DO1","DO2","DO3","DO4","DO5","DO6","DO7","AO0","AO1"])
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget_var.itemChanged.connect(self.update_param_names)
        self.tableWidget_var.itemChanged.connect(self.export_for_pulse_viewer)
        self.tableWidget_var.itemChanged.connect(self.create_python_var)
        self.tableWidget.itemChanged.connect(self.export_for_pulse_viewer)


        self.init_first_col()
        self.init_first_row()

        self.pushButton_stop_acquisition.setEnabled(False)

        self.pushButton_add_col_left.clicked.connect(self.add_column_left)
        self.pushButton_add_col_right.clicked.connect(self.add_column_right)
        self.pushButton_del_col.clicked.connect(self.remove_column)
        self.pushButton_extrract_matrix.clicked.connect(self.click_save_pulse_config)
        self.pushButton_load_config.clicked.connect(self.click_load_from_cfg)
        self.pushButton_move_right.clicked.connect(self.move_column_right)
        self.pushButton_move_left.clicked.connect(self.move_column_left)
        self.pushButton_add_var_down.clicked.connect(self.create_var_down)
        self.pushButton_save_var.clicked.connect(self.click_save_var_config)
        self.pushButton_load_var.clicked.connect(self.click_load_var_from_cfg)
        self.pushButton_plot_pulse.clicked.connect(self.export_for_pulse_viewer)
        self.pushButton_invert.clicked.connect(self.invert_row)
        self.pushButton_pulse_sequence.clicked.connect(self.sequence_preview_button)
        self.pushButton_swap_rows.clicked.connect(self.swap_selected_rows)
        self.pushButton_compute_sequence.clicked.connect(self.sequence_compute_button)
        self.pushButton_start_acquisition.clicked.connect(self.start_acquisition)
        self.pushButton_stop_acquisition.clicked.connect(self.stop_acquisition)
        self.pushButton_stop_acquisition.clicked.connect(self.reset_PS)

        self.spinBox_step.valueChanged.connect(self.update_num_points)
        self.spinBox_num_points.valueChanged.connect(self.update_step)
        self.spinBox_max.valueChanged.connect(self.update_step)
        self.spinBox_min.valueChanged.connect(self.update_step)

        self.actionpulseStreamer.triggered.connect(self.open_PS_config_window)

        self.DAQ_data_curve = self.plotwidget_DAQ_data.plot(pen='y')
        self.DAQ_data_markers = pyqtgraph.ScatterPlotItem(symbol="o")
        self.plotwidget_DAQ_data.addItem(self.DAQ_data_markers)
        self.DAQ_data_curve.setDownsampling(auto=False)

        self.live_data_curve = self.plotwidget_live_data.plot(pen='r')
        self.live_data_markers = pyqtgraph.ScatterPlotItem(symbol="o")
        self.plotwidget_live_data.addItem(self.live_data_markers)
        self.live_data_curve.setDownsampling(auto=False)

        self.DAQ_data_plot_flag = False
        self.live_plot_updating = False



        self.load_var_from_cfg()
        self.load_from_cfg()

        self.final_patterns = [(0,0) for i in range(0,9)]

        self.PS_thread = None

        self.PS_conf_win = None
        self.thread = None
        self.daq = None

        print("[UI] Main thread:", QThread.currentThread())

    def update_step(self):
        start = self.spinBox_min.value()
        stop = self.spinBox_max.value()
        num_points = self.spinBox_num_points.value()
        step = int((stop-start)/num_points)
        self.spinBox_step.setValue(step)

    def update_num_points(self):
        start = self.spinBox_min.value()
        stop = self.spinBox_max.value()
        step = self.spinBox_step.value()
        num_points = int((stop - start) / step)
        self.spinBox_num_points.setValue(num_points)

    def open_explorer_to_save(self, directory = ""):
        """
        Ouvre une fenêtre d'explorateur permettant de créer ou sélectionner un fichier.
        Retourne le chemin sélectionné.
        """
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        options = QFileDialog.Options()
        options |= QFileDialog.DontConfirmOverwrite  # Ne force pas la confirmation d'écrasement

        path_to_file, _ = QFileDialog.getSaveFileName(
            None,
            "Créer ou sélectionner un fichier",
            directory,
            "Fichier de configuration (*.cfg)",
            options=options
        )

        return path_to_file

    def open_explorer_to_load(self, directory=""):
        """
        Ouvre une fenêtre de sélection de fichier et retourne le chemin sélectionné.
        """
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        path_to_file, _ = QFileDialog.getOpenFileName(
            None,
            "Sélectionner un fichier",
            directory,
            "Fichier de configuration (*.cfg)",
            options=options
        )

        return path_to_file

    def open_PS_config_window(self):
        if self.PS_conf_win == None:
            self.PS_conf_win = PS_config_window()
        self.PS_conf_win.show()

    def start_acquisition(self):

        self.init_PS()
        self.signals = SignalInterface()

        self.plot_timer = QTimer(self)
        self.plot_timer.setInterval(300)

        self.continuous_plot_cond = False
        self.live_plot_updating = False
        self.max_data_points = self.spinBox_buffer.value()

        self.live_data = np.empty(self.max_data_points)
        self.live_data[:] = np.nan
        self.live_data_absolute_time = np.empty(self.max_data_points)
        self.live_data_absolute_time[:] = np.nan
        self.live_data_timescale = np.empty(self.max_data_points)
        self.live_data_timescale[:] = np.nan

        self.DAQ_data = np.empty(self.spinBox_num_points.value())
        self.DAQ_data[:] = np.nan
        self.DAQ_data_timestamp = np.empty(self.spinBox_num_points.value())
        self.DAQ_data_timestamp[:] = np.nan

        self.DAQ_data_plot_flag = True

        self.DAQ_data_sampling_rate = 1
        self.prev_idx = 0


        self.thread = QThread()
        self.worker = DAQ_MFLI()
        self.worker.moveToThread(self.thread)

        self.signals.send_params.connect(self.worker.set_parameters)

        # Connect signals
        # self.thread.started.connect(self.worker.run_continuous)

        self.worker.DAQ_data_ready.connect(self.update_DAQ_data)
        self.worker.live_data_ready.connect(self.update_live_data)

        self.plot_timer.timeout.connect(self.update_live_plot)
        self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.plot_timer.stop)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        phase = self.doubleSpinBox_phase.value()
        filter_freq = self.doubleSpinBox_filter_freq.value()
        n_average = self.spinBox_n_average.value()
        n_points = self.spinBox_num_points.value()
        min_time = self.spinBox_min.value()
        max_time = self.spinBox_max.value()





        # self.thread.started.connect(self.worker.run_continuous_dummy)
        self.thread.started.connect(lambda : self.modifie_DAQ_params(phase, filter_freq, n_average, n_points, min_time, max_time))

        # self.thread.started.connect(self.worker.run_continuous_dummy)


        self.plot_timer.start()
        print("[TIMER] plot_timer started")
        print("Timer isActive:", self.plot_timer.isActive())
        print("Connected slots:", self.plot_timer.receivers(self.plot_timer.timeout))
        self.thread.start()


        self.pushButton_start_acquisition.setEnabled(False)
        self.pushButton_stop_acquisition.setEnabled(True)

        self.run_PS_continuous()

    def modifie_DAQ_params(self, phase, filter_freq, n_average, n_points, min_time, max_time):
        params = {"phase" : phase, "filter_freq" : filter_freq, "n_average" : n_average, "n_points" : n_points, "min_time" : min_time, "max_time" : max_time}
        self.signals.send_params.emit(params)


    def update_label(self, data):
        """Update the label when new data is received."""
        self.label_live_data.setText(data)

    def reset_PS(self):
        self.PS_worker.stop_streaming()

    def init_PS(self):
        self.PS_thread = QThread()
        self.PS_worker = PS()
        self.PS_worker.moveToThread(self.PS_thread)
        self.PS_thread.start()

        self.PS_worker.finished.connect(self.PS_thread.quit)
        self.PS_worker.finished.connect(self.PS_worker.deleteLater)
        self.PS_thread.finished.connect(self.PS_thread.deleteLater)

    def run_PS_continuous(self):

        pattern_tuples = self.PS_worker.load_pattern(self.final_patterns)
        self.PS_worker.run_continuous(pattern_tuples)

    def stop_acquisition(self):
        if self.worker:
            self.worker.stop()
        self.DAQ_data_plot_flag = False
        self.pushButton_start_acquisition.setEnabled(True)
        self.pushButton_stop_acquisition.setEnabled(False)
        self.plot_timer.stop()

    def update_live_plot(self):
        # print("trying to plot...")
        # self.DAQ_data_plot = np.copy(self.DAQ_data)
        if self.live_plot_updating:
            print("already plotting")
            return

            # self.DAQ_data_timescale = np.linspace(self.spinBox_min.value(),self.spinBox_min.value()+self.spinBox_step.value()*len(self.DAQ_data), len(self.DAQ_data))
        # self.DAQ_data_timescale = np.linspace(0, self.max_data_points/self.DAQ_data_sampling_rate, self.max_data_points) #for continuous streaming from MFLI
        self.live_plot_updating = True
        try:

            # self.live_data_timescale = np.linspace(0, len(self.live_data)*self.live_sampling_rate, len(self.live_data))
            self.live_data_curve.setData(self.live_data_timescale, self.live_data)
            self.live_data_markers.setData(self.live_data_timescale, self.live_data)


        except Exception as e:
            print("can't plot live data")
            print(f"[Error live plot] {e}")
            pass
        self.live_plot_updating = False

    def update_DAQ_plot(self):
        # self.DAQ_data_plot = np.copy(self.DAQ_data)

        # self.DAQ_data_timescale = np.linspace(self.spinBox_min.value(),self.spinBox_min.value()+self.spinBox_step.value()*len(self.DAQ_data), len(self.DAQ_data))
        # self.DAQ_data_timescale = np.linspace(0, self.max_data_points/self.DAQ_data_sampling_rate, self.max_data_points) #for continuous streaming from MFLI
        try:
            self.DAQ_data_curve.setData(self.DAQ_data_timescale, self.DAQ_data)
            self.DAQ_data_markers.setData(self.DAQ_data_timescale, self.DAQ_data)
            # print("data plotted")
        except Exception as e:
            print("can't plot DAQ data")
            print(f"[Error DAQ plot] {e}")
            pass

    def update_DAQ_data(self, new_value):
        # if self.continuous_plot_cond:
        #     self.DAQ_data = np.roll(self.DAQ_data, -len(new_value[0]))
        #     self.DAQ_data[-len(new_value[0]):] = new_value[0]
        #     self.DAQ_data_sampling_rate = new_value[1]
        #     self.DAQ_data_timescale = np.linspace(0, len(self.DAQ_data)*self.DAQ_data_sampling_rate, len(self.DAQ_data))
        # else:
        self.DAQ_data = new_value[0]
        self.DAQ_data_timescale = new_value[1]
        self.update_DAQ_plot()

    def update_live_data(self, new_value):

        self.live_data = np.roll(self.live_data, -len(new_value[0]))
        self.live_data[-len(new_value[0]):] = new_value[0]
        self.live_data_absolute_time = np.roll(self.live_data_absolute_time, -len(new_value[1]))
        self.live_data_absolute_time[-len(new_value[1]):] = new_value[1]
        self.live_data_timescale = self.live_data_absolute_time - self.live_data_absolute_time[-1]
        # print(self.live_data)







        # self.live_data_sampling_rate = new_value[1]
        # self.live_data_timescale = np.linspace(0, len(self.live_data)*self.live_data_sampling_rate, len(self.live_data))


class SignalInterface(QObject):
    send_params = pyqtSignal(dict)










