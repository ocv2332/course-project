"""Модуль, хранящий в себе методы, связанные с безопасностью"""

import hashlib
import re
import uuid
from typing import Dict


class SecurityUtils:
    """Класс, хранящий в себе методы, связанные с безопасностью"""

    def __init__(self, config):
        self.config = config

    @staticmethod
    def hash_password(password: str) -> str:
        """Метод, хеширующий пароль

        Args:
            password: Пароль для хеширования
        Returns:
            Хешированный пароль
        """

        salt = uuid.uuid4().hex
        return hashlib.sha512(salt.encode() + password.encode()).hexdigest() + ':' + salt

    @staticmethod
    def check_password(hashed_password: str, user_password: str) -> bool:
        """Метод, проверяющий введенный пароль на соответствие с паролем, который хранится в БД

        Args:
            hashed_password: Хешированный пароль
            user_password: Введенный пароль
        Returns:
            True в случае совпадения, False - в ином случае
        """

        password, salt = hashed_password.split(':')
        return password == hashlib.sha512(salt.encode() + user_password.encode()).hexdigest()

    def get_answer_check_password(self, hashed_password: str, entered_password: str) -> str:
        """Метод, возвращающий код в зависимости от сравнения введенного и хешированного паролей

        Args:
            hashed_password: Хешированный пароль
            entered_password: Введенный пароль
        Returns:
            successful_code в случае совпадения, error_code - в ином случае
        """

        if self.check_password(hashed_password, entered_password):
            return self.config.successful_code
        return self.config.error_code

    @staticmethod
    def check_password_steps(password: str) -> Dict[str, bool]:
        """Метод, проверяющий пароль на соответствование требованиям

        Args:
            password: Введенный пароль
        Returns:
            Словарь с значениями типа bool
        """

        length_error = len(password) >= 8
        uppercase_error = re.search(r"[A-Z]", password) is not None
        lowercase_error = re.search(r"[a-z]", password) is not None
        digit_error = re.search(r"\d", password) is not None
        symbol_error = re.search(r"[!@#$%^&*]", password) is not None

        return {
            'length_error': length_error,
            'uppercase_error': uppercase_error,
            'lowercase_error': lowercase_error,
            'digit_error': digit_error,
            'symbol_error': symbol_error,
        }
