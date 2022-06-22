"""Модуль, хранящий в себе методы, использующиеся в сборщике данных"""

import threading
from datetime import datetime
from typing import List, Tuple, Union

from lxml import html
from requests import models, sessions


class ParserUtils:
    """Класс, хранящий в себе методы, использующиеся в сборщике данных"""

    def __init__(self, config):
        self.config = config

    @staticmethod
    def get_datetime_now() -> List[str]:
        """Метод получения текущих даты и времени

        Returns:
            Список с текущими датой и временем

        Examples:
            >>> print(get_datetime_now())
            ['2022-03-22', '15:40']
        """

        datetime_now = str(datetime.now())
        return datetime_now[:datetime_now.rfind(':')].split()

    def get_auth_code(self, response: models.Response) -> int:
        """Метод проверки попытки аутентификации

        Args:
            response: Ответ от POST-запроса
        Returns:
            Число - код, обозначающий итог попытки аутентификации
        """

        if response.json().get('error', 0) == self.config.auth_error:
            return self.config.error_code
        return self.config.successful_code

    @staticmethod
    def get_tree(session: sessions.Session, url: str) -> html.HtmlElement:
        """Метод получения HTML-дерева

        Args:
            session: Объект сессии модуля requests
            url: URL для обращения
        """

        html_document = session.get(url)
        return html.fromstring(html_document.text)

    def get_datetime_and_tree(self, session: sessions.Session, url: str) -> Tuple[str, str, html.HtmlElement]:
        """Метод получения дерева и даты, времени

        Args:
            session: Объект сессии модуля requests
            url: URL для обращения
        """

        date, time = self.get_datetime_now()
        tree = self.get_tree(session, url)
        return date, time, tree

    def get_reset_password_message(self, session: sessions.Session) -> str:
        """Метод получения сообщения во время восстановления пароля

        Args:
            session: Объект сессии модуля requests
        """

        tree = self.get_tree(session, self.config.recovery_url)
        return tree.xpath('//form[@class="access_recovery_form"]/input')[0].get('placeholder')

    @staticmethod
    def check_reset_password_message(message_from_site: str, check_message: str, error_message: str) -> str | None:
        """Метод проверки введенных данных во время восстановления пароля

        Args:
            message_from_site: Сообщение, полученное от сайта
            check_message: Сообщение для проверки
            error_message: Сообщение для вывода в случае ввода ошибочных данных
        """

        if message_from_site == check_message:
            return error_message
        return None

    @staticmethod
    def life_loop_thread(function, join: bool, *args) -> Union[None, threading.Thread]:
        """Метод создания и поддержки жизненного цикла потока

        Args:
            function: Указатель на функцию, запускаемую в потоке
            join: True для ожидания завершения потока, False в ином случае
            *args: Аргументы, передаваемые в функцию
        """

        thread = threading.Thread(target=function, args=args)
        thread.start()

        if not join:
            return thread
        thread.join()
