"""Модуль, хранящий в себе методы, отвечающие за сбор учебных данных"""

import re

import numpy as np
import pandas as pd
from sqlalchemy import select, delete

from config.config import Config
from database import models
from parser._parser_user_settings import ParserUserSettings
from parser.parser_meta import ParserMeta


class Parser(ParserUserSettings, metaclass=ParserMeta):
    """Класс, хранящий в себе методы, отвечающие за сбор учебных данных"""

    def __init__(self, database, config, exceptions, parser_utils, security_utils, secondary_utils):
        super().__init__(database, config, exceptions, parser_utils, security_utils, secondary_utils)

    def auth(self, login: str, password: str) -> str:
        """Метод, отвечающий за авторизацию

        Args:
            login: Введенный логин
            password: Введенный пароль
        Returns:
            Код, отражающий успех авторизации
        """

        if not self.scnt.check_internet_by_url(self.config.url):
            if (auth_data := self.database.get_auth_data(login)) is not None:
                return self.scrt.get_answer_check_password(auth_data[2], password)
            return self.config.error_code

        response = self.session.post(self.config.auth_url, Config.get_auth_data(login, password))
        return self.database.insert_auth_data(response, login, password)

    def get_user_id(self) -> None:
        """Метод, получающий идентификатор пользователя"""

        tree = self.pt.get_tree(self.session, self.config.url)
        self.user_id = re.search(r'sender_id : \d*',
                                 str(tree.xpath('//script[contains(text(), "sender_id")]/text()'))
                                 ).group(0).split(':')[-1].strip()

    def get_csrf(self) -> None:
        """Метод, получающий CSRF-токен"""

        tree = self.pt.get_tree(self.session, self.config.url)
        csrf = str(tree.xpath('//script[contains(text(),"csrf")]/text()'))
        self.csrf = re.search(r'csrf.*,', csrf).group(0)[:-1].split()[-1].replace("'", '')

    def get_groups(self, is_sync: bool = False) -> None:
        """Метод, собирающий все группы

        Args:
            is_sync: Значение, указывающее на необходимость синхронизации данных
        """

        date, time, tree = self.pt.get_datetime_and_tree(self.session, self.config.groups_url.format(course='0'))
        last_course = int(tree.xpath('//select[@name="k"]/option[last()]/text()')[0])
        groups = set()

        for course in np.arange(1, last_course + 1):
            tree = self.pt.get_tree(self.session, self.config.groups_url.format(course=course))

            groups.update(set(tuple([group,
                                     date,
                                     time]) for group in tree.xpath('//table/tr[position() > 1]/td[1]/text()')))

        groups = pd.DataFrame(groups, columns=['group', 'date', 'time'])

        if is_sync:
            self.database.engine_connect(delete(models.Group))

        self.database.to_sql_query(groups, 'groups')

    def get_subjects(self, group: str, is_sync=False) -> None:
        """Метод, собирающий все предметы и семестры группы

        Args:
            group: Название группы
            is_sync: Значение, указывающее на необходимость синхронизации данных
        """

        group_id = self.database.get_group(group)

        if is_sync:
            self.database.engine_connect(delete(models.Subject).where(models.Subject.group == group_id))

        student_id = self.database.get_student_id_by_group(group_id)
        journals_url = self.config.journals_url.format(id=student_id)

        date, time, tree = self.pt.get_datetime_and_tree(self.session, journals_url)

        subjects = tree.xpath('//table/tr[position() > 1]/td[position() = 2]/text()')
        semesters = tree.xpath('//table/tr[position() > 1]/td[position() = 1]/text()')
        urls = tree.xpath('//table/tr[position() > 1]/td[position() = 6]/a')

        subjects = np.unique(np.array([[semesters[index], group_id, subjects[index].rstrip('.'),
                                        self.config.url + urls[index].get('href'), date, time
                                        ] for index in np.arange(0, len(subjects))]), axis=0)

        index = self.database.get_last_index(select(models.Subject.id))
        subjects = pd.DataFrame(subjects, columns=['semester', 'group', 'subject', 'url', 'date', 'time'],
                                index=np.arange(index, index + len(subjects)))

        self.database.to_sql_query(subjects, 'subjects', '')

    def get_students(self, group, is_sync=False) -> None:
        """Метод, собирающий всех студентов группы

        Args:
            group: Название группы
            is_sync: Значение, указывающее на необходимость синхронизации данных
        """

        if is_sync:
            self.database.engine_connect(delete(models.Students
                                                ).where(models.Students.group == self.database.get_group(group)))

        response = self.session.post(self.config.all_users_url, Config.get_search_data(0, group)).json()
        students = [[student['id'], *student['fio'].strip().split()[:3]] for student in response['list']]

        total_students = response['total']
        for offset in np.arange(30, total_students, 30):
            response = self.session.post(self.config.all_users_url, Config.get_search_data(offset, group)).json()
            students += [[student['id'], *student['fio'].strip().split()[:3]] for student in response['list']]

        students = pd.DataFrame(students, columns=['id', 'name', 'surname', 'patronymic'])
        students.insert(0, 'group', self.database.get_group(group))

        date, time = self.pt.get_datetime_now()
        students['date'], students['time'] = date, time

        self.database.to_sql_query(students, 'students')

    def get_marks(self, group: str, semester: int, subject: str, is_sync=False) -> None:
        """Метод, собирающий всех студентов группы

        Args:
            group: Название группы
            semester: Номер семестра
            subject: Название предмета
            is_sync: Значение, указывающее на необходимость синхронизации данных
        """

        group_id = int(self.database.get_group(group))
        subject_id, url = self.database.get_subject((models.Subject.id, models.Subject.url,), subject, semester, group)

        if is_sync:
            self.database.engine_connect(delete(models.Marks).where(models.Marks.group == group_id,
                                                                    models.Marks.subject == subject_id))

        date, time, tree = self.pt.get_datetime_and_tree(self.session, url)
        students = self.database.get_all_students(group)
        index = self.database.get_last_index(select(models.Marks.id))

        dates = [date.strip() for date in tree.xpath('//a[@data-placement="left"]/text()')]

        length_dates = len(dates)
        if length_dates != 0:
            marks = [mark.text_content().strip() for mark in tree.xpath(
                f'//table[@class="fl_left scorestable"]/tbody/tr[position() <= {len(students)}]/td[position() > 1 and position() < last() - 4]')]

            marks = np.array([[index, group_id, students[index // length_dates % len(students)], subject_id, semester,
                               mark, dates[index % length_dates], date, time] for index, mark in
                              enumerate(marks, index)])

            marks = pd.DataFrame(marks, columns=['id', 'group', 'student', 'subject', 'semester', 'mark',
                                                 'lesson_date', 'date', 'time'],
                                 index=np.arange(index, index + len(marks)))

            self.database.to_sql_query(marks, 'marks')
