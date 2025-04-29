from datetime import datetime
from tkinter import READABLE

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum, VARCHAR, Sequence

import enum

from db import SqlAlchemyBase


class TaskStatus(enum.Enum):
    DONE = "DONE"
    PENDING = "PENDING"
    NONE = "NONE"
    CANCELLED = "CANCELLED"


class TaskShareLevel(enum.Enum):
    PARENT_SELECT = 0
    PRIVATE = 128

    R_ALL = 127
    R_ONLY_1_LEVELS = 1
    R_ONLY_2_LEVELS = 2

    RW_ALL = -127
    RW_ONLY_1_LEVELS = -1
    RW_ONLY_2_LEVELS = -2

    @staticmethod
    def level2int(level):
        match level:
            case TaskShareLevel.PARENT_SELECT:
                return 0
            case TaskShareLevel.PRIVATE:
                return 128
            case TaskShareLevel.R_ALL:
                return 127
            case TaskShareLevel.R_ONLY_1_LEVELS:
                return 1
            case TaskShareLevel.R_ONLY_2_LEVELS:
                return 2
            case TaskShareLevel.RW_ALL:
                return -127
            case TaskShareLevel.RW_ONLY_1_LEVELS:
                return -1
            case TaskShareLevel.RW_ONLY_2_LEVELS:
                return 2
            case _:
                return 0

    @staticmethod
    def int2level(level):
        match level:
            case 0:
                return TaskShareLevel.PARENT_SELECT
            case 128:
                return TaskShareLevel.PRIVATE
            case 127:
                return TaskShareLevel.R_ALL
            case 1:
                return TaskShareLevel.R_ONLY_1_LEVELS
            case 2:
                return TaskShareLevel.R_ONLY_2_LEVELS
            case -127:
                return TaskShareLevel.RW_ALL
            case -1:
                return TaskShareLevel.RW_ONLY_1_LEVELS
            case -2:
                return TaskShareLevel.RW_ONLY_2_LEVELS
            case _:
                return 0

    # def __gt__(self, other):
    #     return TaskShareLevel.level2int(self) > TaskShareLevel.level2int(other)
    #
    # def __lt__(self, other):
    #     return TaskShareLevel.level2int(self) < TaskShareLevel.level2int(other)
    #
    # def __gte__(self, other):
    #     return TaskShareLevel.level2int(self) >= TaskShareLevel.level2int(other)
    #
    # def __lte__(self, other):
    #     return TaskShareLevel.level2int(self) <= TaskShareLevel.level2int(other)

    # @staticmethod
    # def is_in(instance, iterable):
    #     for item in iterable:
    #         if isinstance(item, TaskShareLevel) and TaskShareLevel.level2int(item) == TaskShareLevel.level2int(instance):
    #             return True
    #     return False

WRITABLE_POLITICS = [
    TaskShareLevel.RW_ONLY_1_LEVELS,
    TaskShareLevel.RW_ONLY_2_LEVELS,
    TaskShareLevel.RW_ALL,
]

READABLE_POLITICS = [
    TaskShareLevel.R_ONLY_1_LEVELS,
    TaskShareLevel.R_ONLY_2_LEVELS,
    TaskShareLevel.R_ALL,
] + WRITABLE_POLITICS


TABLE_ID = Sequence('table_id_seq', start=1000)

class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'

    id = Column(Integer, TABLE_ID, primary_key=True, server_default=TABLE_ID.next_value())
    # id = Column(Integer, primary_key=True, autoincrement="ignore_fk")
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parent = Column(ForeignKey('tasks.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True, default=None)
    title = Column(VARCHAR(128), nullable=False)
    description = Column(VARCHAR(512), nullable=True, default=None)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.NONE)

    access_politics = Column(Enum(TaskShareLevel), nullable=False, default=TaskShareLevel.PARENT_SELECT)

    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=True, default=datetime.utcnow)

    @property
    def writable(self):
        return self.access_politics in WRITABLE_POLITICS
