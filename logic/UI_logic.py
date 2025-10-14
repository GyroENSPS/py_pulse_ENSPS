from PyQt5.QtWidgets import QCheckBox, QTableWidgetItem, QComboBox, QMainWindow, QMessageBox
from PyQt5.uic.Compiler.qtproxies import QtWidgets
from GUI.UI_files.table_widget_test import Ui_MainWindow
from GUI.UI_files.PS_config_Window_UI import Ui_PS_config_Form
from GUI.PS_config_window import PS_config_window


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