from GUI.UI_files.PS_config_Window_UI import Ui_PS_config_Form
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
import os

class PS_config_window(QWidget, Ui_PS_config_Form):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.PS_config_directory = "hardware_config/PS_config"
        self.PS_config_files = [f for f in os.listdir(self.PS_config_directory) if os.path.isfile(os.path.join(self.PS_config_directory, f))]
        self.comboBox_config_files.addItems(self.PS_config_files)