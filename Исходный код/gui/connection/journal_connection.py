import math

import pandas as pd
from PyQt5 import QtWidgets

from gui.connection.main_connection import MainWindow
from gui.pyqt.tablemodel import TableModel
from gui.windows import journal_window


class JournalWindow(QtWidgets.QMainWindow, journal_window.Ui_JournalWindow):
    def __init__(self, database, config, gui_utils):
        super(JournalWindow, self).__init__()
        self.setupUi(self)

        self.database = database
        self.config = config
        self.gt = gui_utils

        self.MainWindow = MainWindow(config)

    def initialization(self, group, semester, subject):
        get_all_date = self.database.get_data(subject, semester, group)
        dates_length = len(get_all_date)

        if not dates_length:
            return self.gt.create_message_box(QtWidgets.QMessageBox.Information, "Сообщение", "Данная таблица пустая")

        get_all_student = [f"{index}. {full_name}" for index, full_name in
                           enumerate(self.database.get_all_students(group, 'text'), 1)]
        get_all_marks = self.database.get_marks(subject, semester)

        data = pd.DataFrame(
            [[*get_all_marks[index * dates_length:(index + 1) * dates_length]] for index in
             range(len(get_all_student))], columns=get_all_date, index=get_all_student)

        if dates_length < 22:
            width = math.ceil(1100 / dates_length)
        else:
            width = 50

        model = TableModel(data)
        self.table.setModel(model)

        self.table.setStyleSheet("QHeaderView::section { background-color: #ffffff; padding: 4px;"
                                 "border-style: none; border-bottom: 1px solid #d8d8d8; border-right: 1px solid "
                                 "#d8d8d8; } "
                                 "QHeaderView::section:horizontal { border-top: 1px solid #d8d8d8; border-bottom: 1px "
                                 "solid #d8d8d8; color: #337ab7; }"
                                 "QHeaderView::section:vertical { border-left: 1px solid #d8d8d8; }"
                                 "QTableCornerButton::section { background-color: white; border: 1px solid #d8d8d8; }")

        for i in range(len(get_all_date)):
            self.table.setColumnWidth(i, width)
