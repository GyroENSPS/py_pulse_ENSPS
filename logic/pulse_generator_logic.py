import numpy as np
import pyqtgraph
from PyQt5.QtWidgets import QMainWindow, QCheckBox
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from tifffile import enumarg

from GUI.UI_files.table_widget_test import Ui_MainWindow
import matplotlib.pyplot as plt

class PulseGeneratorLogic(QMainWindow, Ui_MainWindow):

    def create_python_var(self):
        row_count = self.tableWidget_var.rowCount()
        var_names = [None] * row_count
        var_values = [None] * row_count
        run_cond = True
        while run_cond:
            run_cond = False
            for row in range(row_count):
                item = self.tableWidget_var.item(row, 0)
                var_name_str = item.text()
                var_names[row] = var_name_str
                item = self.tableWidget_var.item(row, 1)
                var_value_str = item.text()
                # var_name_str = "self.user_var_" + var_name_str
                code_line = var_name_str + "=" + var_value_str

                print(row)
                try:
                    exec(code_line)
                    exec("var_values[row] =" + var_name_str)
                except:
                    run_cond = True
                    print("problem with row ", row)
                    pass

            for var_name in var_names:
                try:
                    exec("print(" + var_name + ")")
                except:
                    print("Problem")
                    pass
        return var_values

    def export_for_pulse_viewer(self):
        self.tabWidget.setCurrentIndex(0)


        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()

        pulse_matrix = np.zeros((10, cols))
        pulse_durations = np.zeros(cols)
        variable_index = []
        pulse_durations_from_user = self.create_python_var()

        for col in range(cols):
            combo = self.tableWidget.cellWidget(0, col)
            idx = combo.currentIndex()
            pulse_durations[col] = pulse_durations_from_user[idx]
            var_checkbox = self.tableWidget_var.cellWidget(idx, 3)
            if isinstance(var_checkbox, QCheckBox):
                if var_checkbox.isChecked():
                    variable_index.append(col)
            for row in range(1,9):
                checkbox = self.tableWidget.cellWidget(row, col)
                if checkbox.isChecked():
                    value = 1
                else :
                    value = 0
                pulse_matrix[row-1][col] = value
            for row in range(9,11):
                item = self.tableWidget.item(row, col)
                try :
                    value = item.text()
                    pulse_matrix[row-1][col] = value
                except:
                    pass
        channel_labels=["DO0","DO1","DO2","DO3","DO4","DO5","DO6","DO7","AO0","AO1"]
        min_meas = self.spinBox_min.value()
        max_meas = self.spinBox_max.value()
        self.pulseViewer(pulse_durations, pulse_matrix, variable_index, "test", channel_labels, min_meas, max_meas)
        # self.sequenceGenerator(pulse_durations, pulse_matrix, variable_index, 10, 1, min_meas, max_meas)


        # print(pulse_durations)
        # print(pulse_matrix)
        # print(variable_index)

    def pulseViewer(self, *args):
        # print(type(args))
        pulses_length_R1234, IO_R1234, variable_index, name, channel_labels, min_measurement, max_measurement = args

        # pulses_length, IO_R1, IO_R2, IO_R3, IO_R4, variable_index, correction, channel_plot_conditions, channel_labels = args


        begin_pulses_length = np.copy(pulses_length_R1234)
        end_pulses_length = np.copy(pulses_length_R1234)
        # for var_idx in variable_index:
        #     pulses_length_R1234[var_idx] = max_measurement
        pulses_timings = [sum(pulses_length_R1234[:i // 2]) for i in range(
            len(pulses_length_R1234) * 2 + 1)]  # calculates the time positions of each pulse edge (oversampling for plotting reasons)
        begin_measurement_range = np.copy(variable_index)
        end_measurement_range = np.copy(variable_index)
        IO_R1234_plot = [None] * len(IO_R1234)

        self.pulse_view.clear()
        for element in variable_index:
            begin_pulses_length[element] = min_measurement  # changes the pulse sequence with the variable parameter
            begin_measurement_range = sum(begin_pulses_length[:element + 1])
            end_pulses_length[element] = max_measurement  # changes the pulse sequence with the variable parameter
            # end_measurement_range = sum(end_pulses_length[:element + 1])
            end_measurement_range = begin_measurement_range + (max_measurement-min_measurement)
            print(begin_measurement_range, end_measurement_range)
            region = pyqtgraph.LinearRegionItem(
                values=(begin_measurement_range, end_measurement_range),
                orientation=pyqtgraph.LinearRegionItem.Vertical
            )
            region.setBrush(pyqtgraph.mkBrush('turquoise'))  # couleur de fond
            region.setOpacity(0.2)  # transparence
            region.setZValue(-10)  # sous la courbe
            region.setMovable(False)  # zone fixe

            # Ajout au graphique
            self.pulse_view.addItem(region)
            begin_pulses_length = np.copy(pulses_length_R1234)
            end_pulses_length = np.copy(pulses_length_R1234)

        # print(begin_measurement_range, end_measurement_range)

        plot_offset = -2.1
        plot_offset_counter = 0


        for i in range(len(IO_R1234)):


            IO_R1234_plot_temp = [IO_R1234[i][j // 2] + plot_offset_counter * plot_offset for j in
                                  range(len(IO_R1234[i]) * 2)]
            IO_R1234_plot_temp.append(IO_R1234_plot_temp[-1])
            IO_R1234_plot[i] = self.rotate(IO_R1234_plot_temp, -1)
            fill_color = QColor(self.channel_colors[i])
            fill_color.setAlphaF(0.2)  # 0.2 = 20% opaque (donc 80% transparent)

            self.pulse_view.plot(pulses_timings, IO_R1234_plot[i], label=channel_labels[i], pen=pyqtgraph.mkPen(color=self.channel_colors[i], width=2), brush = fill_color, fillLevel=plot_offset_counter * plot_offset)

            plot_offset_counter += 1

        color_dash_line = (0, 0, 0, int(255 * 0.2))  # Noir avec alpha 0.2
        line_style = QtCore.Qt.DashLine  # Ligne pointillée
        line_width = 0.5

        # Ajout des lignes verticales
        for x in pulses_timings:
            line = pyqtgraph.InfiniteLine(pos=x, angle=90, pen=pyqtgraph.mkPen(color=color_dash_line, width=line_width, style=line_style))
            self.pulse_view.addItem(line)

    def rotate(self, l, n):
        return l[n:] + l[:n]

    def patternCalculator(self, pulse_list, IO_list):
        # Generates a list of tuples like (pulse duration, output value)
        # print(IO_list)
        pattern = [None] * (len(IO_list) + 1)
        stop_cond_pattern = True
        # print(len(pulse_list))
        j = 0
        k = 0
        while stop_cond_pattern:
            stop_cond_rolling = True
            # print(k)
            pulse_len = pulse_list[k]
            if k < len(pulse_list):
                i = k + 1
                while stop_cond_rolling:
                    # for i in range(k+1,len(pulse_list)):
                    if i == len(pulse_list):
                        pattern[j] = (pulse_len, IO_list[i - 1])

                        stop_cond_pattern = False
                        stop_cond_rolling = False
                        # print("mark 1")
                    elif IO_list[i] == IO_list[i - 1]:
                        pulse_len += pulse_list[i]
                        i += 1
                        # print(pulse_len)
                        # print("mark 2")
                    else:
                        pattern[j] = (pulse_len, IO_list[i - 1])
                        # print(pattern[j])
                        pulse_len = 0
                        j += 1
                        k = i
                        stop_cond_rolling = False
                        # print("mark 3")
            else:
                pattern[j] = (pulse_len, IO_list[k])
                stop_cond_pattern = False

        pulse_len = sum(pulse_list[:]) - sum(pulse_list[:j])
        pattern[j + 1] = (pulse_len, 0)

        pattern = pattern[0:j + 1]

        print(len(pattern))

        return pattern

    def update_pulse_durations(self, names, instructions):
        new_durations = np.zeros(len(instructions))
        run_flag = True
        n = 0
        while run_flag and n<100:
            run_flag = False
            for idx, instruction in enumerate(instructions):
                try:
                    code_line = names[idx]+"="+ instruction
                    # print(code_line)
                    exec(code_line)
                    code_line = "new_durations[idx]="+names[idx]
                    # print(code_line)
                    exec(code_line)
                    # print(new_durations)
                except:
                    run_flag = True
                    n+=1
                    pass

        return new_durations

    def sequence_calculator_button(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()

        pulse_matrix = np.zeros((10, cols))
        pulse_durations = np.zeros(cols)
        variable_index = []
        pulse_durations_from_user = self.create_python_var()
        param_per_col = [None]*cols

        for col in range(cols):
            combo = self.tableWidget.cellWidget(0, col)
            idx = combo.currentIndex()
            param_per_col[col] = idx
            pulse_durations[col] = pulse_durations_from_user[idx]
            var_checkbox = self.tableWidget_var.cellWidget(idx, 3)
            if isinstance(var_checkbox, QCheckBox):
                if var_checkbox.isChecked():
                    variable_index.append(col)
            for row in range(1, 9):
                checkbox = self.tableWidget.cellWidget(row, col)
                if checkbox.isChecked():
                    value = 1
                else:
                    value = 0
                pulse_matrix[row - 1][col] = value
            for row in range(9, 11):
                item = self.tableWidget.item(row, col)
                try:
                    value = item.text()
                    pulse_matrix[row - 1][col] = value
                except:
                    pass
        channel_labels = ["DO0", "DO1", "DO2", "DO3", "DO4", "DO5", "DO6", "DO7", "AO0", "AO1"]
        min_meas = self.spinBox_min.value()
        max_meas = self.spinBox_max.value()
        step_meas = self.spinBox_step.value()
        # self.pulseViewer(pulse_durations, pulse_matrix, variable_index, "test", channel_labels, min_meas, max_meas)
        num_meas_points = int((max_meas - min_meas)/step_meas)
        print("number of measurement points : ", num_meas_points)
        self.sequenceGenerator(pulse_durations, pulse_matrix, variable_index, param_per_col, num_meas_points, 1, min_meas, max_meas)

    def sequence_preview_button(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()

        pulse_matrix = np.zeros((10, cols))
        pulse_durations = np.zeros(cols)
        variable_index = []
        pulse_durations_from_user = self.create_python_var()
        param_per_col = [None]*cols

        for col in range(cols):
            combo = self.tableWidget.cellWidget(0, col)
            idx = combo.currentIndex()
            param_per_col[col] = idx
            pulse_durations[col] = pulse_durations_from_user[idx]
            var_checkbox = self.tableWidget_var.cellWidget(idx, 3)
            if isinstance(var_checkbox, QCheckBox):
                if var_checkbox.isChecked():
                    variable_index.append(col)
            for row in range(1, 9):
                checkbox = self.tableWidget.cellWidget(row, col)
                if checkbox.isChecked():
                    value = 1
                else:
                    value = 0
                pulse_matrix[row - 1][col] = value
            for row in range(9, 11):
                item = self.tableWidget.item(row, col)
                try:
                    value = item.text()
                    pulse_matrix[row - 1][col] = value
                except:
                    pass
        channel_labels = ["DO0", "DO1", "DO2", "DO3", "DO4", "DO5", "DO6", "DO7", "AO0", "AO1"]
        min_meas = self.spinBox_min.value()
        max_meas = self.spinBox_max.value()
        step_meas = self.spinBox_step.value()
        n_repeat = self.spinBox_n_repeat.value()
        num_meas_points = self.spinBox_num_points.value()

        print("number of measurement points : ", num_meas_points)
        self.sequenceGenerator(pulse_durations, pulse_matrix, variable_index, param_per_col, 10, n_repeat, min_meas, max_meas, plot_cond=True)

    def sequence_compute_button(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()

        pulse_matrix = np.zeros((10, cols))
        pulse_durations = np.zeros(cols)
        variable_index = []
        pulse_durations_from_user = self.create_python_var()
        param_per_col = [None]*cols

        for col in range(cols):
            combo = self.tableWidget.cellWidget(0, col)
            idx = combo.currentIndex()
            param_per_col[col] = idx
            pulse_durations[col] = pulse_durations_from_user[idx]
            var_checkbox = self.tableWidget_var.cellWidget(idx, 3)
            if isinstance(var_checkbox, QCheckBox):
                if var_checkbox.isChecked():
                    variable_index.append(col)
            for row in range(1, 9):
                checkbox = self.tableWidget.cellWidget(row, col)
                if checkbox.isChecked():
                    value = 1
                else:
                    value = 0
                pulse_matrix[row - 1][col] = value
            for row in range(9, 11):
                item = self.tableWidget.item(row, col)
                try:
                    value = item.text()
                    pulse_matrix[row - 1][col] = value
                except:
                    pass
        channel_labels = ["DO0", "DO1", "DO2", "DO3", "DO4", "DO5", "DO6", "DO7", "AO0", "AO1"]
        min_meas = self.spinBox_min.value()
        max_meas = self.spinBox_max.value()
        step_meas = self.spinBox_step.value()
        n_repeat = self.spinBox_n_repeat.value()
        num_meas_points = self.spinBox_num_points.value()

        print("number of measurement points : ", num_meas_points)
        self.final_sequenceGenerator(pulse_durations, pulse_matrix, variable_index, param_per_col, num_meas_points, n_repeat, min_meas, max_meas)


    def sequenceGenerator(self, pulses_length, IO_states, var_index, param_per_col, num_of_points, n_repeat, min_meas, max_meas, plot_cond = False):
        ############# Generate measurement sequences

        point_trigger_channel = self.comboBox_trigger_per_point_channel.currentIndex()
        point_trigger_duration = self.spinBox_trigger_per_point_duration.value()
        sequence_trigger_channel = self.comboBox_trigger_per_sequence_channel.currentIndex()
        sequence_trigger_duration = self.spinBox_trigger_per_sequence_duration.value()

        row_count = self.tableWidget_var.rowCount()
        var_names = [None]*row_count
        var_instructions = [None]*row_count
        var_conds_idx = []
        for row in range(row_count):
            item = self.tableWidget_var.item(row, 0)
            var_names[row] =  item.text()
            item = self.tableWidget_var.item(row, 1)
            var_instructions[row] = item.text()
            checkbox = self.tableWidget_var.cellWidget(row, 3)
            if checkbox.isChecked():
                var_conds_idx.append(row)

        # print(var_names, var_instructions, var_conds_idx)
        meas_points = np.linspace(min_meas, max_meas, num_of_points, dtype=int)
        print(meas_points)
        all_pulses_durations = np.zeros(len(pulses_length)*num_of_points*n_repeat)
        point_trigger_timings = np.zeros(2 * num_of_points)
        point_trigger_IO = np.zeros(2 * num_of_points)

        for idx, point in enumerate(meas_points):
            for i in var_conds_idx:
                var_instructions[i] = str(point)
            new_params = self.update_pulse_durations(var_names, var_instructions)
            new_durations = np.copy(pulses_length)
            for idx_param, param_number in enumerate(param_per_col):
                new_durations[idx_param] = new_params[param_number]
            # print(new_durations)
            point_trigger_timings[idx*2:idx*2+2] = [point_trigger_duration, sum(new_durations)*n_repeat-point_trigger_duration]
            point_trigger_IO[idx * 2:idx * 2 + 2] = [0, 1]
            for repeat_idx in range(n_repeat):
                first_index = (idx * n_repeat + repeat_idx) * len(pulses_length)
                last_index = (idx * n_repeat + repeat_idx + 1) * len(pulses_length)
                all_pulses_durations[first_index:last_index] = new_durations
        # print(all_pulses_durations)

        sequence_trigger_timings = [sequence_trigger_duration, sum(all_pulses_durations)-sequence_trigger_duration]
        sequence_trigger_IO = [1, 0]


        matrix_shape = np.shape(IO_states)
        all_IO_states =  np.tile(IO_states, (1, num_of_points*n_repeat))
        # print(np.array_str(all_IO_states))

        final_patterns = [None] * len(all_IO_states)
        self.pulse_sequence_view.clear()
        plot_offset = -2.1
        for i in range(len(all_IO_states)):
            if i == point_trigger_channel:
                final_patterns[i] = self.patternCalculator(point_trigger_timings, point_trigger_IO)
            elif i == sequence_trigger_channel:
                final_patterns[i] = self.patternCalculator(sequence_trigger_timings, sequence_trigger_IO)
            else:
                final_patterns[i] = self.patternCalculator(all_pulses_durations, all_IO_states[i])

            if plot_cond:
                self.patternViewer(final_patterns[i], i * plot_offset, self.channel_colors[i])

    def final_sequenceGenerator(self, pulses_length, IO_states, var_index, param_per_col, num_of_points, n_repeat, min_meas, max_meas, plot_cond = False):
        ############# Generate measurement sequences

        point_trigger_channel = self.comboBox_trigger_per_point_channel.currentIndex()
        point_trigger_duration = self.spinBox_trigger_per_point_duration.value()
        sequence_trigger_channel = self.comboBox_trigger_per_sequence_channel.currentIndex()
        sequence_trigger_duration = self.spinBox_trigger_per_sequence_duration.value()

        row_count = self.tableWidget_var.rowCount()
        var_names = [None]*row_count
        var_instructions = [None]*row_count
        var_conds_idx = []
        for row in range(row_count):
            item = self.tableWidget_var.item(row, 0)
            var_names[row] =  item.text()
            item = self.tableWidget_var.item(row, 1)
            var_instructions[row] = item.text()
            checkbox = self.tableWidget_var.cellWidget(row, 3)
            if checkbox.isChecked():
                var_conds_idx.append(row)

        # print(var_names, var_instructions, var_conds_idx)
        meas_points = np.linspace(min_meas, max_meas, num_of_points, dtype=int)
        print(meas_points)
        all_pulses_durations = np.zeros(len(pulses_length)*num_of_points*n_repeat)
        point_trigger_timings = np.zeros(2 * num_of_points)
        point_trigger_IO = np.zeros(2 * num_of_points)

        for idx, point in enumerate(meas_points):
            for i in var_conds_idx:
                var_instructions[i] = str(point)
            new_params = self.update_pulse_durations(var_names, var_instructions)
            new_durations = np.copy(pulses_length)
            for idx_param, param_number in enumerate(param_per_col):
                new_durations[idx_param] = new_params[param_number]
            # print(new_durations)
            point_trigger_timings[idx*2:idx*2+2] = [point_trigger_duration, sum(new_durations)*n_repeat-point_trigger_duration]
            point_trigger_IO[idx * 2:idx * 2 + 2] = [0, 1]
            for repeat_idx in range(n_repeat):
                first_index = (idx * n_repeat + repeat_idx) * len(pulses_length)
                last_index = (idx * n_repeat + repeat_idx + 1) * len(pulses_length)
                all_pulses_durations[first_index:last_index] = new_durations
        # print(all_pulses_durations)

        sequence_trigger_timings = [sequence_trigger_duration, sum(all_pulses_durations)-sequence_trigger_duration]
        sequence_trigger_IO = [1, 0]


        matrix_shape = np.shape(IO_states)
        all_IO_states =  np.tile(IO_states, (1, num_of_points*n_repeat))
        # print(np.array_str(all_IO_states))

        final_patterns = [None] * len(all_IO_states)
        self.pulse_sequence_view.clear()
        plot_offset = -2.1
        total_tuple_length = 0
        total_measurement_time = sum(sequence_trigger_timings) * self.spinBox_n_average.value()
        for i in range(len(all_IO_states)):
            if i == point_trigger_channel:
                final_patterns[i] = self.patternCalculator(point_trigger_timings, point_trigger_IO)
            elif i == sequence_trigger_channel:
                final_patterns[i] = self.patternCalculator(sequence_trigger_timings, sequence_trigger_IO)
            else:
                final_patterns[i] = self.patternCalculator(all_pulses_durations, all_IO_states[i])

            if plot_cond:
                self.patternViewer(final_patterns[i], i * plot_offset, self.channel_colors[i])
            total_tuple_length += len(final_patterns[i])
        self.label_num_tupple.setText(str(total_tuple_length))
        self.label_total_time.setText(str(int(total_measurement_time*1e-9))+"s")
        self.final_patterns = final_patterns



    def patternViewer(self, pattern, plot_offset, channel_color, channel_label = ""):

        IO_R1234 = [tupple[1] for tupple in pattern]
        # print(np.shape(IO_R1234))
        pulse_length = [tupple[0] for tupple in pattern]
        pulses_timings = [sum(pulse_length[:i // 2]) for i in range(
            len(pulse_length) * 2 + 1)]

        IO_R1234_plot_temp = [IO_R1234[j // 2] + plot_offset for j in
                              range(len(IO_R1234) * 2)]
        IO_R1234_plot_temp.append(IO_R1234_plot_temp[-1])
        IO_R1234_plot = self.rotate(IO_R1234_plot_temp, -1)
        fill_color = QColor(channel_color)
        fill_color.setAlphaF(0.2)  # 0.2 = 20% opaque (donc 80% transparent)

        self.pulse_sequence_view.plot(pulses_timings, IO_R1234_plot, label=channel_label,
                             pen=pyqtgraph.mkPen(color=channel_color, width=2), brush=fill_color,
                             fillLevel=plot_offset)

    def patternCalculator(self, pulse_list, IO_list):
        # Generates a list of tuples like (pulse duration, output value)
        # print(IO_list)
        pattern = [None] * (len(IO_list) + 1)
        stop_cond_pattern = True
        # print(len(pulse_list))
        j = 0
        k = 0
        while stop_cond_pattern:
            stop_cond_rolling = True
            # print(k)
            pulse_len = pulse_list[k]
            if k < len(pulse_list):
                i = k + 1
                while stop_cond_rolling:
                    # for i in range(k+1,len(pulse_list)):
                    if i == len(pulse_list):
                        pattern[j] = (pulse_len, IO_list[i - 1])

                        stop_cond_pattern = False
                        stop_cond_rolling = False
                        # print("mark 1")
                    elif IO_list[i] == IO_list[i - 1]:
                        pulse_len += pulse_list[i]
                        i += 1
                        # print(pulse_len)
                        # print("mark 2")
                    else:
                        pattern[j] = (pulse_len, IO_list[i - 1])
                        # print(pattern[j])
                        pulse_len = 0
                        j += 1
                        k = i
                        stop_cond_rolling = False
                        # print("mark 3")
            else:
                pattern[j] = (pulse_len, IO_list[k])
                stop_cond_pattern = False

        pulse_len = sum(pulse_list[:]) - sum(pulse_list[:j])
        pattern[j + 1] = (pulse_len, 0)

        pattern = pattern[0:j + 1]

        print(len(pattern))

        return pattern



