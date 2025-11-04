import sys
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


class DAQWorker(QObject):
    # Signal pour démarrer la méthode avec des paramètres
    start_requested = pyqtSignal(float, float)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = False
        self.start_requested.connect(self.run_continuous)

    @pyqtSlot(float, float)
    def run_continuous(self, phase, filter_freq):
        print(f"[Worker] Démarrage avec phase={phase}, filtre={filter_freq}")
        self.running = True
        t = 0
        while self.running and t < 5:
            print(f"[Worker] t = {t:.1f}s - phase={phase}, filt={filter_freq}")
            time.sleep(1)
            t += 1
        print("[Worker] Fin de la boucle")
        self.finished.emit()

    def stop(self):
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Thread DAQ")

        # Un bouton pour lancer l'acquisition
        self.button = QPushButton("Démarrer l'acquisition", self)
        self.button.clicked.connect(self.start_acquisition)
        self.setCentralWidget(self.button)

    def start_acquisition(self):
        # Paramètres venant de l'interface
        phase = 0.5
        filter_freq = 10.0

        # Créer thread + worker
        self.thread = QThread()
        self.worker = DAQWorker()
        self.worker.moveToThread(self.thread)

        # Nettoyage à la fin
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Démarrer le thread et envoyer les paramètres après le start
        self.thread.started.connect(lambda: self.worker.start_requested.emit(phase, filter_freq))

        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
