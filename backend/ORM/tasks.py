from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum, VARCHAR
from sqlalchemy.orm import relationship
from flask_login import UserMixin

import enum

from db import SqlAlchemyBase


class TaskStatus(enum.Enum):
    DONE = "DONE"
    PENDING = "PENDING"
    NONE = "NONE"
    CANCELLED = "CANCELLED"


class TaskShareLevel(enum.Enum):
    PARENT_SELECT = 0

    R_ALL = 128
    R_ONLY_1_LEVELS = 1
    R_ONLY_2_LEVELS = 2

    RW_ALL = -128
    RW_ONLY_1_LEVELS = -1
    RW_ONLY_2_LEVELS = -2


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parent = Column(ForeignKey('tasks.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True, default=None)
    title = Column(VARCHAR(128), nullable=False)
    description = Column(VARCHAR(512), nullable=True, default=None)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.NONE)

    access_politics = Column(Enum(TaskShareLevel), nullable=False, default=TaskShareLevel.PARENT_SELECT)

    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=True, default=datetime.utcnow)
