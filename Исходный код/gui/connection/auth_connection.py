from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog
from sqlalchemy import select

from config.config import Config
from database import models
from gui.connection.journal_connection import JournalWindow
from gui.connection.main_connection import MainWindow
from gui.connection.recovery_connection import RecoveryWindow
from gui.pyqt.roundpixmapstyle import RoundPixmapStyle
from gui.windows import login_window
from parser.parser import Parser


class AuthWindow(QtWidgets.QDialog, login_window.Ui_Authorization):
    def __init__(self, config, database, exceptions, parser_utils, security_utils, secondary_utils, gui_utils):
        super(AuthWindow, self).__init__()

        self.config = config
        self.database = database
        self.exceptions = exceptions

        self.pt = parser_utils
        self.scrt = security_utils
        self.scnt = secondary_utils
        self.gt = gui_utils

        self.parser = Parser(database, config, exceptions, parser_utils, security_utils, secondary_utils)

        self.setupUi(self)

        self.MainWindow = MainWindow(config)
        self.JournalWindow = JournalWindow(database, config, gui_utils)
        self.RecoveryWindow = RecoveryWindow(config, database, exceptions, parser_utils,
                                             security_utils, secondary_utils)

        self.icon.setPixmap(QtGui.QPixmap("gui/icons/logo.svg"))
        self.visibleIcon = QIcon("gui/icons/visible_icon.svg")

        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.toggleShowPassword = self.password.addAction(self.visibleIcon, QtWidgets.QLineEdit.TrailingPosition)
        self.toggleShowPassword.triggered.connect(self.show_password)
        self.toggleBool = False

        self.entry.clicked.connect(self.auth)
        self.remember.clicked.connect(self.show_recovery_window)

        self.MainWindow.profile_menu.clicked.connect(lambda: self.change_page('profile'))
        self.MainWindow.journal_menu.clicked.connect(lambda: self.change_page('journal'))
        self.MainWindow.settings_menu.clicked.connect(self.developed_page)
        self.MainWindow.help_menu.clicked.connect(lambda: self.change_page('about'))
        self.MainWindow.settings.clicked.connect(lambda: self.change_page('change'))

        self.MainWindow.image_change.clicked.connect(self.change_image_profile)
        self.MainWindow.email_change.clicked.connect(self.change_email)
        self.MainWindow.password_change.clicked.connect(self.change_password)

        self.MainWindow.journal_open.clicked.connect(self.fill_journal)

        self.MainWindow.group_sync.clicked.connect(self.synchronization_group)
        self.MainWindow.subject_sync.clicked.connect(self.synchronization_subjects_and_semesters)

        self.MainWindow.help_password.installEventFilter(self)
        self.login.installEventFilter(self)
        self.password.installEventFilter(self)

        self.MainWindow.password_entry.textChanged.connect(self.check_password)

        self.completed_requirements = []

    def developed_page(self):
        msg = self.gt.create_message_box(QtWidgets.QMessageBox.Information,
                                         "Разработка", "Данное окно находится на стадии разработки")
        msg.exec_()

    def eventFilter(self, source, event):
        if source is self.login and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Down:
            self.password.setFocus()
            return True
        elif source is self.password and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Up:
            self.login.setFocus()
            return True

        elif source is self.MainWindow.help_password:
            if event.type() == QEvent.Enter:
                self.MainWindow.password_help.show()
                return True
            elif event.type() == QEvent.Leave:
                self.MainWindow.password_help.hide()
        return False

    def check_password(self):
        keys = Config.get_objects_password_requirements(self.MainWindow)
        messages = Config.get_password_requirements(self.config)
        current_password = self.MainWindow.password_entry.text()

        self.completed_requirements = {key: value for key, value in
                                       zip(keys, list(self.scrt.check_password_steps(current_password).values()))}

        for index, (key, value) in enumerate(self.completed_requirements.items()):
            self.gt.set_color_and_text(key, messages[index], self.config, value)

        self.MainWindow.password_check.setValue(sum(self.completed_requirements.values()) * 20)
        self.gt.set_color_bar(self.MainWindow.password_check)

    def show_password(self):
        self.gt.get_password_visibility_settings(self.password, self.toggleShowPassword, self.toggleBool)
        self.toggleBool = not self.toggleBool

    def synchronization_group(self):
        self.parser.get_groups(True)

    def synchronization_subjects_and_semesters(self):
        group = self.MainWindow.group_choice.currentText()
        self.parser.get_subjects(group, True)

    def change_page(self, window):
        self.MainWindow.stackedWidget.setCurrentIndex(Config.get_page_index()[window])

    def show_recovery_window(self):
        self.parser.get_csrf()
        self.RecoveryWindow.show()

    def fill_about_user(self, information):
        user_information = Config.get_user_information(self.MainWindow, information)

        for key, value in user_information.items():
            key.clear()
            key.setText(value)

    def change_image_profile(self):
        file_path = QFileDialog.getOpenFileName(self, "Выбор фотографии", "./", self.config.file_extensions)[0]

        if file_path:
            self.parser.change_avatar(file_path)
            file_extension = self.scnt.get_file_extension(file_path)

            with open(file_path, "rb") as new_file, open(rf'data\user_avatar.{file_extension}', 'wb') as old_file:
                old_file.write(new_file.read())

            if file_extension == 'gif':
                self.scnt.set_and_start_gif(self.MainWindow)
            else:
                self.MainWindow.image.setPixmap(self.MainWindow.circleImage(rf'data/user_avatar.{file_extension}'))

    def change_email(self):
        email = self.MainWindow.email_entry.text()
        self.parser.change_email(email)

    def change_password(self):
        password = self.MainWindow.password_entry.text()

        if all(self.completed_requirements):
            msg = self.gt.create_message_box(QtWidgets.QMessageBox.Warning,
                                             self.config.error_message, self.config.change_password_error)
            msg.exec_()
            return None

        self.parser.change_password(password)
        self.MainWindow.password_entry.clear()

    def fill_combobox_group(self):
        get_all_groups = self.database.get_all_groups()

        self.MainWindow.group_choice.clear()
        self.MainWindow.group_choice.addItems([self.config.select_group_message] + get_all_groups)

        self.MainWindow.group_choice.currentIndexChanged.connect(self.fill_combobox_semester)

    def fill_combobox_semester(self):
        self.MainWindow.semester_choice.clear()
        group = self.MainWindow.group_choice.currentText()
        group_id = self.database.get_group(group)

        if self.database.select_query(select(models.Students).where(models.Students.group == group_id), 2) is None:
            self.parser.get_students(group)

        if self.database.select_query(select(models.Subject).where(models.Subject.group == group_id), 2) is None:
            self.parser.get_subjects(group)

        get_all_semester = self.database.get_all_semesters(group)

        self.MainWindow.semester_choice.addItems([self.config.select_semester_message] + get_all_semester)
        self.MainWindow.semester_choice.currentIndexChanged.connect(self.fill_combobox_subject)

    def fill_combobox_subject(self):
        group = self.MainWindow.group_choice.currentText()
        semester = self.MainWindow.semester_choice.currentText()
        get_all_subject = self.database.get_all_subjects(group, int(semester), 'text')

        self.MainWindow.subject_choice.clear()
        self.MainWindow.subject_choice.addItems([self.config.select_subject_message] + get_all_subject)

    def fill_journal(self):
        group = self.MainWindow.group_choice.currentText()
        semester = self.MainWindow.semester_choice.currentText()
        subject = self.MainWindow.subject_choice.currentText()

        group_id = self.database.get_group(group)
        subject_id = self.database.get_subject((models.Subject.id,), subject, semester, group)[0]
        if self.database.select_query(select(models.Marks).where(models.Marks.group == group_id,
                                                                 models.Marks.semester == int(semester),
                                                                 models.Marks.subject == subject_id), 2) is None:
            self.parser.get_marks(group, int(semester), subject)

        self.JournalWindow.journal_info.setText(
            f"Группа: <b>{group}</b>; Дисциплина: <b>{subject}</b>; Семестр: <b>{semester}</b>;")
        # self.JournalWindow.journal_teacher.setText(f"Преподаватели: <font color='blue'> Юренская </font>")
        answer = self.JournalWindow.initialization(group, semester, subject)

        if isinstance(answer, QtWidgets.QMessageBox):
            answer.exec_()
        else:
            self.JournalWindow.show()

    def auth(self):
        LOGIN = self.login.text()
        PASSWORD = self.password.text()
        CODE = self.parser.auth(LOGIN, PASSWORD)

        if CODE != self.config.successful_code:
            msg = self.gt.create_message_box(QtWidgets.QMessageBox.Warning,
                                             self.config.error_message, self.config.auth_error)
            msg.exec_()
        else:
            self.parser.get_user_id()
            self.parser.get_csrf()

            if self.database.select_query(select(models.Group), 2) is None:
                self.parser.get_groups()

            info_about_user = self.parser.get_full_info_about_auth_user()
            self.fill_about_user(info_about_user)

            self.scnt.create_dir('data')
            url_user_avatar = self.parser.get_user_avatar()
            self.scnt.get_image(self.config.url + url_user_avatar)
            file_extension = self.scnt.get_file_extension(url_user_avatar)

            if file_extension == 'gif':
                proxy_style = RoundPixmapStyle(radius=65, style=self.MainWindow.image.style())
                self.MainWindow.image.setStyle(proxy_style)
                self.scnt.set_and_start_gif(self.MainWindow)
            else:
                self.MainWindow.image.setPixmap(self.MainWindow.circleImage(rf'data\user_avatar.{file_extension}'))

            self.fill_combobox_group()

            self.close()
            self.MainWindow.show()
