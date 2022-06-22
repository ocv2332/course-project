from sqlalchemy import String, Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    group = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    semester = Column(String, nullable=False)
    group = Column(String, ForeignKey(Group.id, ondelete="CASCADE"))
    subject = Column(String, nullable=False)
    url = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)


class Students(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    group = Column(String, ForeignKey(Group.id, ondelete="CASCADE"))
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    patronymic = Column(String)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)


class Marks(Base):
    __tablename__ = 'marks'

    id = Column(Integer, primary_key=True)
    group = Column(String, ForeignKey(Group.id, ondelete="CASCADE"))
    student = Column(String, ForeignKey(Students.id, ondelete="CASCADE"))
    subject = Column(String, ForeignKey(Subject.id, ondelete="CASCADE"))
    semester = Column(String, nullable=False)
    mark = Column(String, nullable=False)
    lesson_date = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)


class Authorized(Base):
    __tablename__ = 'auth_users'

    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
