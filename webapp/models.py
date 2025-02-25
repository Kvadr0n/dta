import enum

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from flask import current_app as app


Base = declarative_base()


def create_session_manually(connection_string: str) -> Session:
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return factory()


def create_session() -> Session:
    connection_string = app.config["CONNECTION_STRING"]
    return create_session_manually(connection_string)


class Group(Base):
    __tablename__ = "groups"
    id = sa.Column("id", sa.Integer, primary_key=True, nullable=False)
    title = sa.Column("title", sa.String, unique=True, nullable=False)


class Task(Base):
    __tablename__ = "tasks"
    id = sa.Column("id", sa.Integer, primary_key=True, nullable=False)


class Variant(Base):
    __tablename__ = "variants"
    id = sa.Column("id", sa.Integer, primary_key=True, nullable=False)


class IntEnum(sa.TypeDecorator):
    impl = sa.Integer
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value
        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)


class TaskStatusEnum(enum.IntEnum):
    Submitted = 0
    Checking = 1
    Checked = 2
    Failed = 3
    NotSubmitted = 4

    @property
    def name(self):
        return {
            self.Submitted: "Отправлено",
            self.Checking: "Проверяется",
            self.Checked: "Принято",
            self.Failed: "Ошибка!",
            self.NotSubmitted: "Не отправлено",
        }[self]

    @property
    def code(self):
        return {
            self.Submitted: "?",
            self.Checking: "...",
            self.Checked: "+",
            self.Failed: "x",
            self.NotSubmitted: "-",
        }[self]

    @property
    def color(self):
        return {
            self.Submitted: "primary",
            self.Checking: "warning",
            self.Checked: "success",
            self.Failed: "danger",
            self.NotSubmitted: "secondary",
        }[self]


class TaskStatus(Base):
    __tablename__ = "task_statuses"
    task = sa.Column(
        "task",
        sa.Integer,
        sa.ForeignKey("tasks.id"),
        primary_key=True,
        nullable=False,
    )
    variant = sa.Column(
        "variant",
        sa.Integer,
        sa.ForeignKey("variants.id"),
        primary_key=True,
        nullable=False,
    )
    group = sa.Column(
        "group",
        sa.Integer,
        sa.ForeignKey("groups.id"),
        primary_key=True,
        nullable=False,
    )
    time = sa.Column("time", sa.DateTime, nullable=False)
    code = sa.Column("code", sa.String, nullable=False)
    output = sa.Column("output", sa.String, nullable=True)
    status: sa.Column[TaskStatusEnum] = sa.Column(
        "status",
        IntEnum(TaskStatusEnum),
        nullable=False
    )


class Message(Base):
    __tablename__ = "messages"
    id = sa.Column("id", sa.Integer, primary_key=True, nullable=False)
    task = sa.Column(
        "task",
        sa.Integer,
        sa.ForeignKey("tasks.id"),
        nullable=False,
    )
    variant = sa.Column(
        "variant",
        sa.Integer,
        sa.ForeignKey("variants.id"),
        nullable=False,
    )
    group = sa.Column(
        "group",
        sa.Integer,
        sa.ForeignKey("groups.id"),
        nullable=False,
    )
    time = sa.Column("time", sa.DateTime, nullable=False)
    code = sa.Column("code", sa.String, nullable=False)
    ip = sa.Column("ip", sa.String, nullable=False)
    processed = sa.Column("processed", sa.Boolean, nullable=False)

    def __str__(self):
        return str({
            "id": self.id,
            "task": self.task,
            "variant": self.variant,
            "group": self.group,
            "time": self.time,
            "ip": self.ip,
            "processed": self.processed,
        })
