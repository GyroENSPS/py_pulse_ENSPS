import configparser

from PyQt5.QtWidgets import QCheckBox, QTableWidgetItem, QComboBox, QMainWindow, QMessageBox
from PyQt5.uic.Compiler.qtproxies import QtWidgets
from GUI.UI_files.table_widget_test import Ui_MainWindow


class PulseTableLogic(QMainWindow, Ui_MainWindow):
    def init_first_col(self):
        self.create_column(0)

    def swap_selected_rows(self):
        """
        Échange les contenus de deux lignes sélectionnées dans un QTableWidget.

        :param table_widget: Le QTableWidget concerné
        """
        selected_rows = sorted(set(index.row() for index in self.tableWidget.selectedIndexes()))

        for index in self.tableWidget.selectedIndexes():
            row = index.row()
            if row == 9 or row == 10:
                QMessageBox.warning(self.tableWidget, "Error", "Select only digital channels")
                return

        if len(selected_rows) != 2:
            QMessageBox.warning(self.tableWidget, "Error", "Please, select exactly two lines")
            return

        top_row, bottom_row = selected_rows

        row1, row2 = self.copy_digital_row(top_row), self.copy_digital_row(bottom_row)

        self.paste_digital_row(bottom_row, row1)
        self.paste_digital_row(top_row, row2)


    def create_checkbox(self, row, col_index):
        btn = QCheckBox()
        btn.setStyleSheet("""
                                        QCheckBox::indicator {
                                            width: 100px;
                                            height: 30px;
                                        }

                                        QCheckBox::indicator:unchecked {
                                            image: none;
                                            border: black;
                                            background-color: black;
                                        }

                                        QCheckBox::indicator:checked {
                                            image: none;
                                            border: black;
                                            background-color: """ + self.channel_colors[row - 1] + """;
                                        }
                                    """)
        btn.stateChanged.connect(lambda _, r=row, c=col_index: self.bouton_clique())
        return btn

    def create_combobox(self, col_idx):
        combo = QComboBox()
        combo.addItems(self.list_variable_names)
        combo.activated.connect(lambda index, c=combo: self.bouton_clique())

        return combo

    def change_combobox_idx(self, old_idx, new_idx):
        col_count = self.tableWidget.columnCount()
        for col_idx in range(col_count):
            combo = self.tableWidget.cellWidget(0, col_idx)
            cur_idx = combo.currentIndex()
            if cur_idx == old_idx:
                combo. setCurrentIndex(new_idx)




    def create_column(self, col_idx):
        combo = self.create_combobox(col_idx)
        self.tableWidget.setCellWidget(0, col_idx, combo)
        for row in range(1, 9):
            btn = self.create_checkbox(row, col_idx)
            self.tableWidget.setCellWidget(row, col_idx, btn)
            self.tableWidget.setHorizontalHeaderItem(col_idx, QTableWidgetItem(str(col_idx)))
            self.tableWidget.resizeColumnsToContents()
        for row in range(10,11):
            self.tableWidget.setItem(row, col_idx, QTableWidgetItem("0"))


    def add_column_left(self):
        col_index = self.tableWidget.currentColumn()
        if col_index == -1:
            print("no column selected")
            return
        self.tableWidget.insertColumn(col_index)
        self.create_column(col_index)


    def add_column_right(self):
        col_index = self.tableWidget.currentColumn()
        if col_index == -1:
            print("no column selected")
            return
        col_index += 1
        self.tableWidget.insertColumn(col_index)
        self.create_column(col_index)

    def remove_column(self):
        col_index = self.tableWidget.currentColumn()
        if col_index == -1:
            print("no column selected")
            return
        self.tableWidget.removeColumn(col_index)

    def invert_row(self):
        row_idx = self.tableWidget.currentRow()
        col_count = self.tableWidget.columnCount()
        for col in range(col_count):
            widget = self.tableWidget.cellWidget(row_idx, col)
            if isinstance(widget, QComboBox):
                print("Impossible to invert")
                return
            elif isinstance(widget, QCheckBox):
                valeur = widget.isChecked()
                widget.setChecked(not valeur)
            else:
                item = self.tableWidget.item(row_idx, col)
                valeur = -1*float(item.text())
                self.tableWidget.setItem(row_idx, col, QTableWidgetItem(str(valeur)))


    def bouton_clique(self):
        try:
            print("bouton_clique")
            self.update_tab_display()
        except:
            pass

    def click_save_pulse_config(self):
        path = self.open_explorer_to_save(directory = "pulse_config")
        self.save_pulse_config(path)

    def save_pulse_config(self, path):

        config = configparser.ConfigParser()

        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        headers = [str(col) for col in range(cols)]
        print(headers)


        matrice = []


        for row in range(rows):
            section_name = self.tableWidget.verticalHeaderItem(row).text()
            config[section_name] = {}
            ligne = []
            for col in range(cols):
                widget = self.tableWidget.cellWidget(row, col)
                if isinstance(widget, QComboBox):
                    valeur = widget.currentIndex()
                    valeur = str(valeur)
                elif isinstance(widget, QCheckBox):
                    valeur = widget.isChecked()
                    valeur = str(valeur)
                else:
                    item = self.tableWidget.item(row, col)
                    valeur = item.text() if item else ""  #

                config[section_name][headers[col]] = valeur
                ligne.append(valeur)
            matrice.append(ligne)


        with open(path, "w", encoding="utf-8") as configfile:
            config.write(configfile)

        print("✅ Config file exported as ", path)
        print(matrice)

        return matrice

    def click_load_from_cfg(self):
        path = self.open_explorer_to_load(directory = "pulse_config")
        self.load_from_cfg(path)


    def load_from_cfg(self, path="pulse_config/default_pulse.cfg"):
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
        print("pulses : ", headers)
        row_count = len(sections)
        col_count = len(headers)

        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(col_count)
        self.tableWidget.setHorizontalHeaderLabels(headers)
        for col_idx, key in enumerate(headers):
            col_data = []
            for row_idx, section in enumerate(sections):
                col_data.append(config.get(section, key, fallback = ""))

            self.create_column(col_idx)
            self.fill_column(col_data, col_idx)

    def copy_digital_row(self, index):
        col_count = self.tableWidget.columnCount()
        row = []
        for col in range(col_count):
            widget = self.tableWidget.cellWidget(index, col)
            valeur = widget.isChecked()
            valeur = str(valeur)
            row.append(valeur)
        return row

    def paste_digital_row(self, index, new_row):
        col_count = len(new_row)
        for col in range(col_count):
            widget = self.tableWidget.cellWidget(index, col)
            widget.setChecked(new_row[col].strip().lower() == "true")

    def copy_column(self, index):
        row_count = self.tableWidget.rowCount()
        col = []
        for row in range(row_count):
            widget = self.tableWidget.cellWidget(row, index)
            if isinstance(widget, QCheckBox):
                valeur = widget.isChecked()
                valeur = str(valeur)
            elif isinstance(widget, QComboBox):
                valeur = widget.currentIndex()
                valeur = str(valeur)
            else:
                item = self.tableWidget.item(row, index)
                valeur = item.text() if item else "0"  #
            col.append(valeur)
        return col

    def fill_column(self, col_data, col_idx):
        row_count = self.tableWidget.rowCount()

        for row_idx in range(row_count):
            widget = self.tableWidget.cellWidget(row_idx, col_idx)
            value = col_data[row_idx]
            if isinstance(widget, QCheckBox):
                bool_val = value == "True"
                widget.setChecked(bool_val)
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(int(value))
            elif value == "" :
                value = "0"
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(value))
            else:
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(value))

    def move_column_right(self):
        table = self.tableWidget
        index = table.currentColumn()

        col_count = table.columnCount()
        row_count = table.rowCount()

        if index >= col_count - 1:
            print("❌ Impossible to move column to the right")
            return

        # 1. Copier les deux colonnes concernées

        col_1 = self.copy_column(index)
        col_2 = self.copy_column(index+1)


        # 2. Copier les headers si définis
        header_1 = table.horizontalHeaderItem(index).text() if table.horizontalHeaderItem(index) else ""
        header_2 = table.horizontalHeaderItem(index + 1).text() if table.horizontalHeaderItem(index + 1) else ""

        # 3. Échanger les contenus
        self.fill_column(col_1, index+1)
        self.fill_column(col_2, index)


        # 4. Échanger les en-têtes
        table.setHorizontalHeaderItem(index, QTableWidgetItem(header_2))
        table.setHorizontalHeaderItem(index + 1, QTableWidgetItem(header_1))
        table.setCurrentCell(0, index+1)

    def move_column_left(self):
        table = self.tableWidget
        index = table.currentColumn()

        col_count = table.columnCount()
        row_count = table.rowCount()

        if index <= 0 :
            print("❌ Impossible to move column to the left")
            return

        # 1. Copier les deux colonnes concernées

        col_1 = self.copy_column(index)
        col_2 = self.copy_column(index-1)


        # 2. Copier les headers si définis
        header_1 = table.horizontalHeaderItem(index).text() if table.horizontalHeaderItem(index) else ""
        header_2 = table.horizontalHeaderItem(index - 1).text() if table.horizontalHeaderItem(index - 1) else ""

        # 3. Échanger les contenus
        self.fill_column(col_1, index-1)
        self.fill_column(col_2, index)


        # 4. Échanger les en-têtes
        table.setHorizontalHeaderItem(index, QTableWidgetItem(header_2))
        table.setHorizontalHeaderItem(index - 1, QTableWidgetItem(header_1))
        table.setCurrentCell(0, index - 1)