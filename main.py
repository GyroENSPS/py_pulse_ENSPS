from PyQt5 import QtWidgets
from PyQt5.QtCore import QLocale

QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

import sys
from GUI.main_window import MainWindow

from logic.DAQ_logic import DAQ_MFLI

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()


window.show()
app.exec_()