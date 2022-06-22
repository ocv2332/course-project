"""Модуль, хранящий в себе методы, отвечающие за сбор данных об аккаунте"""

import re

import requests

from config.config import Config


class ParserUserSettings:
    """Класс, хранящий в себе методы, отвечающие за сбор данных об аккаунте"""

    def __init__(self, database, config, exceptions, parser_utils, security_utils, secondary_utils):
        self.config = config
        self.database = database
        self.exceptions = exceptions

        self.pt = parser_utils
        self.scrt = security_utils
        self.scnt = secondary_utils

        self.session = requests.Session()
        self.session.headers = Config.get_headers_data(config.accept, config.user_agent)

        self.csrf = None
        self.user_id = None

    def get_full_info_about_auth_user(self) -> list:
        """Метод, отвечающий за сбор данных с главной страницы профиля пользователя

        Returns:
            Список с собранными данными
        """

        tree = self.pt.get_tree(self.session, self.config.user_url)
        return [check.strip() for check in tree.xpath('//div[@class="info"]/text()[normalize-space()]')]

    def get_user_avatar(self) -> str:
        """Метод, отвечающий за сбор фотографии пользователя

        Returns:
            URL-адрес фотографии
        """

        tree = self.pt.get_tree(self.session, self.config.user_url)
        return re.search(r"'([\S]+?)'",
                         tree.xpath('//div[@class="user_rating"]/div[@class="users_avatar_wrap"]')[0].get('onclick')
                         ).group(0)[1:-1]

    def reset_password_get_email(self, email: str) -> None:
        """Метод, отвечающий за восстановление доступа к аккаунту (ввод электронной почты)

        Args:
            email: Введенная электронная почта
        """

        self.exceptions.check_none(self.csrf)

        response = self.session.post(self.config.recovery_url,
                                     Config.get_reset_password_data(email, self.csrf))

        self.pt.check_reset_password_message(self.pt.get_reset_password_message(self.session),
                                             self.config.enter_email_message,
                                             self.config.email_error)

        code = input(self.config.enter_code_message + ": ")
        self.pt.life_loop_thread(self.reset_password_get_code, True, response, code)

    def reset_password_get_code(self, response: requests.models.Response, code: str) -> None:
        """Метод, отвечающий за восстановление доступа к аккаунту (ввод кода восстановления)

        Args:
            response:
            code: Введенный код восстановления
        """

        self.exceptions.check_none(self.csrf)

        self.session.post(self.config.recovery_url,
                          Config.get_recovery_code_data(code, self.csrf),
                          cookies=response.cookies)

        self.pt.check_reset_password_message(self.pt.get_reset_password_message(self.session),
                                             self.config.enter_code_message,
                                             self.config.code_message_error)

    def change_avatar(self, path_image: str) -> None:
        """Метод, отвечающий за смену фотографии профиля

        Args:
            path_image: Путь до фотографии
        """

        response = self.session.post(self.config.upload_photo_url.format(id=self.user_id),
                                     files={'avatar_file': open(path_image, 'rb')})
        change_avatar = f'/{response.json()["files"][0]["file"]}'
        self.session.post(self.config.profile_data_url, {'change_avatar': change_avatar, 'csrf': self.csrf},
                          cookies=response.cookies)

    def change_email(self, email: str):
        """Метод, отвечающий за смену электронной почты

        Args:
            email: Введенная электронная почта
        """

        self.exceptions.check_none(self.csrf)

        self.session.post(self.config.profile_data_url,
                          Config.get_change_email_data(email, self.csrf))

    def change_password(self, password: str):
        """Метод, отвечающий за смену пароля

        Args:
            password: Введенный пароль
        """

        self.session.post(self.config.profile_data_url,
                          Config.get_change_password_data(password, self.csrf))
