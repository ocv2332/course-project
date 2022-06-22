import os
from itertools import chain

import sqlalchemy.engine
from sqlalchemy import create_engine, MetaData, select, insert, update
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.sql.functions import coalesce

from database import models


class DataBase:
    def __init__(self, name, config, parser_utils, security_utils, exceptions):
        self.name = name
        self.metadata = MetaData()
        self.engine = create_engine(f'sqlite:///{name}')

        self.config = config
        self.parser_utils = parser_utils
        self.security_utils = security_utils
        self.exceptions = exceptions

    @staticmethod
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def create_all_tables(self):
        if not os.path.exists(self.name):
            models.Base.metadata.create_all(self.engine)

    def engine_connect(self, query, is_return=False) -> sqlalchemy.engine.CursorResult | None:
        with self.engine.connect() as connection:
            if is_return:
                return connection.execute(query)
            connection.execute(query)

    def select_query(self, query, return_type: int):
        self.exceptions.check_value_by_number_range((1, 2), return_type)
        with self.engine.connect() as connection:
            if return_type == 1:
                return connection.execute(query).fetchall()
            elif return_type == 2:
                return connection.execute(query).fetchone()

    def insert_query(self, table, *args):
        self.engine_connect(insert(table).values(args))

    def to_sql_query(self, table_object, table_name: str, index=None):
        with self.engine.connect() as connection:
            if index is None:
                table_object.to_sql(table_name, con=connection, if_exists='append', index=False)
            else:
                table_object.to_sql(table_name, con=connection, if_exists='append', index_label='id')

    def get_last_index(self, query):
        with self.engine.connect() as connection:
            try:
                index = int(sorted([index[0] for index in connection.execute(query).fetchall()])[-1]) + 1
            except IndexError:
                index = 0
        return index

    def get_all_groups(self):
        return list(chain.from_iterable(self.select_query(select(models.Group.group), 1)))

    def get_all_semesters(self, group: str):
        return list(chain.from_iterable(self.select_query(select(models.Subject.semester
                                                                 ).where(models.Subject.group == self.get_group(group)
                                                                         ).distinct(), 1)))

    def get_all_subjects(self, group: str, semester: int, return_value: str = None):
        select_query = models.Subject.subject if return_value == 'text' else models.Subject.id
        return list(chain.from_iterable(self.select_query(select(select_query
                                                                 ).where(models.Subject.group == self.get_group(group),
                                                                         models.Subject.semester == semester), 1)))

    def get_all_students(self, group: str, return_value: str = None):
        group_id = self.get_group(group)
        if return_value == "text":
            iterator = iter(list(chain.from_iterable(
                self.select_query(select(models.Students.name,
                                         models.Students.surname,
                                         coalesce(models.Students.patronymic, '')
                                         ).where(models.Students.group == group_id), 1))))
            return [' '.join(name).strip() for name in zip(iterator, iterator, iterator)]
        return list(chain.from_iterable(self.select_query(select(models.Students.id
                                                                 ).where(models.Students.group == group_id), 1)))

    def get_group(self, group: str | int):
        if isinstance(group, int):
            select_query, where_query = models.Group.group, models.Group.id
        else:
            select_query, where_query = models.Group.id, models.Group.group
        return self.select_query(select(select_query).where(where_query == group), 2)[0]

    def get_subject(self, select_query: tuple, subject: str, semester, group):
        return self.select_query(select(*select_query).where(models.Subject.semester == semester,
                                                             models.Subject.subject == subject,
                                                             models.Subject.group == self.get_group(group)), 2)

    def get_auth_data(self, login):
        return self.select_query(select(models.Authorized).where(models.Authorized.login == login), 2)

    def insert_auth_data(self, response, login, password):
        if str(code := self.parser_utils.get_auth_code(response)) == self.config.successful_code:
            hashed_password = self.security_utils.hash_password(password)
            last_index = self.get_last_index(select(models.Authorized.id))
            date, time = self.parser_utils.get_datetime_now()

            if self.get_auth_data(login) is None:
                self.insert_query(models.Authorized, last_index, login, hashed_password, date, time)
            else:
                self.engine_connect(update(models.Authorized).where(models.Authorized.login == login
                                                                    ).values(password=hashed_password,
                                                                             date=date,
                                                                             time=time))
        return code

    def get_student_id_by_group(self, group_id: int):
        return self.select_query(select(models.Students.id).where(models.Students.group == group_id), 2)[0]

    def get_data(self, subject: str, semester: str, group: str):
        subject_id = self.select_query(select(models.Subject.id).where(models.Subject.subject == subject,
                                                                       models.Subject.semester == semester), 2)[0]
        student_id = self.get_student_id_by_group(self.get_group(group))

        return list(chain.from_iterable(self.select_query(select(models.Marks.lesson_date
                                                                 ).where(models.Marks.subject == subject_id,
                                                                         models.Marks.semester == semester,
                                                                         models.Marks.student == student_id), 1)))

    def get_marks(self, subject: str, semester: str):
        subject_id = self.select_query(select(models.Subject.id).where(models.Subject.subject == subject,
                                                                       models.Subject.semester == semester), 2)[0]
        return list(chain.from_iterable(self.select_query(select(models.Marks.mark
                                                                 ).where(models.Marks.subject == subject_id,
                                                                         models.Marks.semester == semester), 1)))
