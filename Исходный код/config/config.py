from PyQt5 import QtWidgets


class Config:
    @staticmethod
    def get_auth_data(login, password):
        return {
            'login': login,
            'pass': password,
            'auth': '1',
            'ajax': '1'
        }

    @staticmethod
    def get_headers_data(accept, user_agent):
        return {
            'accept': accept,
            'user-agent': user_agent
        }

    @staticmethod
    def get_reset_password_data(email, csrf):
        return {
            'recoverystr': email,
            'csrf': csrf,
            'checkrecover': 'Применить'
        }

    @staticmethod
    def get_recovery_code_data(code, csrf):
        return {
            'recoverycode': code,
            'csrf': csrf,
            'checkcode': 'Применить'
        }

    @staticmethod
    def get_change_password_data(password, csrf):
        return {
            'changepass': '1',
            'newpass': password,
            'csrf': csrf
        }

    @staticmethod
    def get_change_email_data(email, csrf):
        return {
            'changemail': '1',
            'mail': email,
            'aj': '1',
            'csrf': csrf
        }

    @staticmethod
    def get_search_data(offset, group):
        return {
            'searchPeople': '1', 'limit': '30',
            'offset': f'{offset}', 'str': f'!{group}',
            'type': '0', 'online': '0'
        }

    @staticmethod
    def get_page_index():
        return {
            'profile': 0,
            'journal': 1,
            'change': 2,
            'settings': 3,
            'about': 4
        }

    @staticmethod
    def get_user_information(window_object, information):
        return {window_object.name: f"<b>{information[0]} {information[1]}</b>",
                window_object.date: f"{information[3]}",
                window_object.group: f"{information[7]}",
                window_object.institute_about: f"{information[4]}",
                window_object.specialization_about: f"{information[5]}",
                window_object.training_about: f"{information[9]}",
                window_object.profile_about: f"{information[6]}",
                window_object.year_about: f"{information[8]}",
                window_object.email_entry: f"{information[10]}"}

    @staticmethod
    def get_password_requirements(config):
        return [config.password_length_message, config.password_uppercase_message,
                config.password_lowercase_message, config.password_digit_message,
                config.password_symbol_message]

    @staticmethod
    def get_objects_password_requirements(window_object: QtWidgets):
        return [window_object.size_text, window_object.capital_text, window_object.lower_text,
                window_object.number_text, window_object.special_text]
