"""Модуль, хранящий в себе вспомогательные методы"""

import os

import requests
from PyQt5 import QtGui


class SecondaryUtils:
    """Класс, хранящий в себе вспомогательные методы"""

    def __init__(self):
        pass

    @staticmethod
    def check_internet_by_url(url: str) -> bool:
        """Метод проверки подключения к Интернету

        Args:
            url: URL для отправки запроса
        Returns:
            True - в случае удачной попытки отправки запроса, False - в ином случае
        """

        try:
            requests.get(url)
            return True
        except requests.ConnectionError:
            return False

    def get_image(self, url: str) -> None:
        """Метод получения фотографии пользователя с портала

        Args:
            url: URL для отправки запроса
        """

        response = requests.get(url)
        with open(rf"data\user_avatar.{self.get_file_extension(url)}", "wb") as file:
            file.write(response.content)

    @staticmethod
    def create_dir(dir_path: str) -> None:
        """Метод создания директории

        Args:
            dir_path: Путь для создания директории
        """

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Метод получения расширения файла

        Args:
            filename: Имя файла
        Returns:
            Расширение файла без точки
        """

        return filename[filename.rfind('.') + 1:]

    @staticmethod
    def set_and_start_gif(window_object) -> None:
        """Метод создания и запуска gif-анимации

        Args:
            window_object: Объект окна, в котором создается gif-анимация
        """

        path = r'data/user_avatar.gif'
        gif = QtGui.QMovie(path)
        window_object.image.setMovie(gif)
        gif.start()
