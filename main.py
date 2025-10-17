from PyQt5 import QtWidgets

import sys
from GUI.main_window import MainWindow

from logic.DAQ_logic import DAQ_MFLI

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()


window.show()
app.exec_()