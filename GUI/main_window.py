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

from logic.pulse_generator_logic import PulseGeneratorLogic
from logic.pulse_table_logic import PulseTableLogic
from logic.var_table_logic import VarTableLogic


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
        self.pushButton_pulse_sequence.clicked.connect(self.sequence_plotter_button)
        self.pushButton_swap_rows.clicked.connect(self.swap_selected_rows)


        self.load_var_from_cfg()
        self.load_from_cfg()

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






