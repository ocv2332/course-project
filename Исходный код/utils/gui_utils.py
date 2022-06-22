"""Модуль, хранящий в себе методы, использующиеся в графическом интерфейсе"""

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QAction, QProgressBar, QMessageBox


class GuiUtils:
    """Класс, хранящий в себе методы, использующиеся в графическом интерфейсе"""

    def __init__(self):
        pass

    @staticmethod
    def set_color_and_text(widget: QtWidgets, message: str, config, bool_value: bool) -> None:
        """Метод, меняющий текст и его цвет в виджете в зависимости от значения переменной типа bool

        Args:
            widget: Виджет, в котором меняются стили и текст
            message: Новый текст
            config: Объект класса, хранящий считанный .ini файл
            bool_value: Переменная-сигнал
        """

        if bool_value:
            widget.setStyleSheet(config.green_color)
            widget.setText(f"✓ {message}")
        else:
            widget.setStyleSheet(config.red_color)
            widget.setText(f"× {message}")

    @staticmethod
    def get_password_visibility_settings(password_obj: QLineEdit, icon_obj: QAction, visibility: bool):
        """Метод, отображающий/скрывающий вводимый пароль

        Args:
            password_obj: Объект, в который вводится пароль
            icon_obj: Объект иконки, отвечающей за отображение/скрытие пароля
            visibility: Переменная-сигнал
        """

        visible_icon = QIcon("gui/icons/visible_icon.svg")
        hidden_icon = QIcon("gui/icons/hidden_icon.svg")

        match visibility:
            case True:
                password_obj.setEchoMode(QLineEdit.Password)
                icon_obj.setIcon(visible_icon)
            case _:
                password_obj.setEchoMode(QLineEdit.Normal)
                icon_obj.setIcon(hidden_icon)

    @staticmethod
    def set_color_bar(progressbar_object: QProgressBar):
        """Метод, изменяющий цвет прогрессбара

        Args:
            progressbar_object: Объект прогрессбара
        """

        match progressbar_object.value():
            case 100:
                progressbar_object.setStyleSheet("QProgressBar::chunk:horizontal { background-color: green; }")
            case num if 50 <= num < 100:
                progressbar_object.setStyleSheet("QProgressBar::chunk:horizontal { background-color: yellow; }")
            case _:
                progressbar_object.setStyleSheet("QProgressBar::chunk:horizontal { background-color: red; }")

    @staticmethod
    def create_message_box(icon: QMessageBox, title: str, text: str):
        """Метод, изменяющий цвет прогрессбара

        Args:
            icon: Иконка окна
            title: Название окна
            text: Текст ошибки
        """

        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        return msg
