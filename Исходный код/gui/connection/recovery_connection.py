from PyQt5 import QtWidgets, QtGui

from config.config import Config
from gui.windows import recovery_window
from parser.parser import Parser


class RecoveryWindow(QtWidgets.QMainWindow, recovery_window.Ui_RecoveryWindow):
    def __init__(self, config, database, exceptions, parser_utils, security_utils, secondary_utils):
        super(RecoveryWindow, self).__init__()

        self.parser = Parser(database, config, exceptions, parser_utils, security_utils, secondary_utils)

        self.setupUi(self)

        self.response = None
        self.text_color = QtGui.QColor("red")

        self.email_apply.clicked.connect(self.show_recovery_email)
        self.code_apply.clicked.connect(self.show_recovery_code)

    def reset_password_get_email(self, email: str):
        self.parser.exceptions.check_none(self.parser.csrf)

        self.response = self.parser.session.post(self.parser.config.recovery_url,
                                                 Config.get_reset_password_data(email, self.parser.csrf))

    def reset_password_get_code(self, code: str):
        self.parser.exceptions.check_none(self.parser.csrf)

        self.parser.session.post(self.parser.config.recovery_url,
                                 Config.get_recovery_code_data(code, self.parser.csrf),
                                 cookies=self.response.cookies)

    def show_recovery_email(self):
        self.parser.get_csrf()

        EMAIL = self.email_input.text()
        self.reset_password_get_email(EMAIL)

        if self.parser.pt.check_reset_password_message(self.parser.pt.get_reset_password_message(self.parser.session),
                                                       self.parser.config.enter_email_message,
                                                       self.parser.config.email_error) is not None:
            self.email_input.clear()
            self.email_input.setPlaceholderText(self.parser.config.email_error)

            pal = self.email_input.palette()
            pal.setColor(QtGui.QPalette.PlaceholderText, self.text_color)
            self.email_input.setPalette(pal)
        else:
            self.stackedWidget.setCurrentIndex(1)

    def show_recovery_code(self):
        self.parser.get_csrf()

        CODE = self.code_input.text()
        self.reset_password_get_code(CODE)

        if self.parser.pt.check_reset_password_message(self.parser.pt.get_reset_password_message(self.parser.session),
                                                       self.parser.config.enter_code_message,
                                                       self.parser.config.code_message_error) is not None:
            self.code_input.clear()
            self.code_input.setPlaceholderText(self.parser.config.code_message_error)

            pal = self.code_input.palette()
            pal.setColor(QtGui.QPalette.PlaceholderText, self.text_color)
            self.code_input.setPalette(pal)
        else:
            self.close()
