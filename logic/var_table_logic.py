import configparser

from PyQt5.QtWidgets import QMainWindow, QCheckBox, QTableWidgetItem
from sympy.parsing.maxima import var_name

from GUI.UI_files.table_widget_test import Ui_MainWindow

class VarTableLogic(QMainWindow, Ui_MainWindow):

    def init_first_row(self):
        self.create_var(0)

    def update_param_names(self):
        self.list_variable_names = []
        cols = self.tableWidget.columnCount()

        for row in range(self.tableWidget_var.rowCount()):
            item = self.tableWidget_var.item(row, 0)
            if item is not None:
                self.list_variable_names.append(item.text())
            else:
                self.list_variable_names.append("")
        for col in range(cols):
            combo = self.tableWidget.cellWidget(0, col)
            idx = combo.currentIndex()
            combo.clear()
            combo.addItems(self.list_variable_names)
            combo.setCurrentIndex(idx)






    def create_var_down(self):
        row_idx = self.tableWidget_var.rowCount()
        if row_idx == -1:
            print("no row selected")
            return
        self.tableWidget_var.insertRow(row_idx)
        self.create_var(row_idx)

    def create_var(self, row_idx):
        var_name = "param_" + str(row_idx)
        self.tableWidget_var.setItem(row_idx, 0, QTableWidgetItem(var_name))
        btn = QCheckBox()
        btn.clicked.connect(lambda _, r=row_idx, c=3: self.var_bouton_clique(r, c))
        self.tableWidget_var.setCellWidget(row_idx, 3, btn)

    def click_load_var_from_cfg(self):
        path = self.open_explorer_to_load(directory = "var_config")
        self.load_var_from_cfg(path)

    def load_var_from_cfg(self, path="var_config/default_var.cfg"):
        config = configparser.ConfigParser()
        with open(path, "r", encoding="utf-8") as f:
            config.read_file(f)
        sections = config.sections()
        print("channels : ", sections)
        if not sections:
            print("❌ Aucun contenu trouvé dans le fichier .cfg.")
            return

        # Utiliser les clés de la première section comme en-têtes
        headers = list(config[sections[0]].keys())
        print("variables : ", headers)
        row_count = len(headers)
        col_count = len(sections)

        self.tableWidget_var.clear()
        self.tableWidget_var.setRowCount(row_count)
        self.tableWidget_var.setColumnCount(col_count)
        self.tableWidget_var.setHorizontalHeaderLabels(sections)
        for row_idx, key in enumerate(headers):
            row_data = []
            for col_idx, section in enumerate(sections):
                row_data.append(config.get(section, key, fallback = ""))

            self.create_var(row_idx)
            self.fill_row(row_data, row_idx)

    def fill_row(self, row_data, row_idx):
        col_count = self.tableWidget_var.columnCount()

        for col_idx in range(col_count):
            widget = self.tableWidget_var.cellWidget(row_idx, col_idx)
            value = row_data[col_idx]
            if isinstance(widget, QCheckBox):
                bool_val = value == "True"
                widget.setChecked(bool_val)
            else :
                self.tableWidget_var.setItem(row_idx, col_idx, QTableWidgetItem(value))

    def click_save_var_config(self):
        path = self.open_explorer_to_save(directory = "var_config")
        self.save_var_config(path)

    def save_var_config(self, path):

        config = configparser.ConfigParser()

        rows = self.tableWidget_var.rowCount()
        cols = self.tableWidget_var.columnCount()
        headers = [str(row) for row in range(rows)]
        print(headers)


        matrice = []

        for col in range(cols):
            section_name = self.tableWidget_var.horizontalHeaderItem(col).text()
            config[section_name] = {}
            ligne = []
            for row in range(rows):

                widget = self.tableWidget_var.cellWidget(row, col)
                if isinstance(widget, QCheckBox):
                    valeur = widget.isChecked()
                    valeur = str(valeur)
                else:
                    item = self.tableWidget_var.item(row, col)
                    valeur = item.text() if item else "0"  #

                config[section_name][headers[row]] = valeur
                ligne.append(valeur)
            matrice.append(ligne)


        with open(path, "w", encoding="utf-8") as configfile:
            config.write(configfile)

        print("✅ Config file exported as 'var_table_export.cfg'")
        print(matrice)

        return matrice


    def var_bouton_clique(self, r, c):
        pass

