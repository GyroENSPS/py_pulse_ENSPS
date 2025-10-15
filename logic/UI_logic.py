import time

import numpy as np
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QCheckBox, QTableWidgetItem, QComboBox, QMainWindow, QMessageBox
from PyQt5.uic.Compiler.qtproxies import QtWidgets
from GUI.UI_files.table_widget_test import Ui_MainWindow
from GUI.UI_files.PS_config_Window_UI import Ui_PS_config_Form
from GUI.PS_config_window import PS_config_window
from logic.DAQ_logic import DAQ_MFLI


class UI_general_logic(QMainWindow, Ui_MainWindow):

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

        self.max_data_points = 10000
        self.DAQ_data = np.empty(self.max_data_points)
        self.DAQ_data[:] = np.nan
        self.DAQ_data_timestamp = np.empty(self.max_data_points)
        self.DAQ_data_timestamp[:] = np.nan
        self.DAQ_data_plot_flag = True
        self.timer = QTimer()
        self.timer.setInterval(300)
        self.DAQ_data_sampling_rate = 1


        self.thread = QThread()
        self.worker = DAQ_MFLI()
        self.worker.moveToThread(self.thread)

        # Connect signals
        # self.thread.started.connect(self.worker.run_continuous)
        self.thread.started.connect(self.worker.run_triggered)
        self.worker.data_ready.connect(self.update_data)
        self.timer.timeout.connect(self.update_plot)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        self.timer.start()

        self.pushButton_start_acquisition.setEnabled(False)
        self.pushButton_stop_acquisition.setEnabled(True)

    def update_label(self, data):
        """Update the label when new data is received."""
        self.label_live_data.setText(data)

    def stop_acquisition(self):
        if self.worker:
            self.worker.stop()
        self.DAQ_data_plot_flag = False
        self.pushButton_start_acquisition.setEnabled(True)
        self.pushButton_stop_acquisition.setEnabled(False)
        self.timer.stop()

    def update_plot(self):
        # self.DAQ_data_plot = np.copy(self.DAQ_data)

        self.DAQ_data_timescale = np.linspace(self.spinBox_min.value(),self.spinBox_min.value()+self.spinBox_step.value()*len(self.DAQ_data), len(self.DAQ_data))
        # self.DAQ_data_timescale = np.linspace(0, self.max_data_points/self.DAQ_data_sampling_rate, self.max_data_points) #for continuous streaming from MFLI
        self.DAQ_data_curve.setData(self.DAQ_data_timescale, self.DAQ_data)


    def update_data(self, new_value):
        self.DAQ_data = np.roll(self.DAQ_data, -len(new_value[0]))
        self.DAQ_data[-len(new_value[0]):] = new_value[0]
        self.DAQ_data_sampling_rate = new_value[1]


