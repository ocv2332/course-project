"""Модуль, хранящий в себе методы для работы с исключениями и сами исключения"""

import os
from typing import Any


class AuthError(Exception):
    """Исключение, указывающее на ошибку авторизации"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Exceptions:
    """Класс, хранящий в себе методы для работы с исключениями"""

    def __init__(self, config):
        self.config = config

    def check_file_path(self, file_path: str):
        """Метод проверки существования файла

        Args:
            file_path: Путь до файла
        Raises:
            FileNotFoundError: Если файла не существует
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(self.config.file_not_found_error)

    def check_auth(self, response_code: str):
        """Метод проверки успеха авторизации

        Args:
            response_code: Код ответа от сервера
        Raises:
            AuthError: Если авторизация не пройдена
        """

        if response_code != self.config.successful_code:
            raise AuthError(self.config.auth_error)

    def check_none(self, value: Any):
        """Метод проверки значения на None-значение

        Args:
            value: Переданное значение
        Raises:
            ValueError: Если переменная - None
        """

        if value is None:
            raise ValueError(self.config.none_value_error)

    def check_value_by_number_range(self, number_range: tuple, value: int):
        """Метод проверки вхождения значения в интервал

        Args:
            number_range: Интервал значений
            value: Значение для проверки
        Raises:
            ValueError: Если значение value не входит в number_range
        """

        if value not in number_range:
            raise ValueError(self.config.value_error.format(possible_values=number_range))
