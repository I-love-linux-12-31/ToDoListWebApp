from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum, VARCHAR
from flask_login import UserMixin

from db import SqlAlchemyBase

class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(64), unique=True)
    email = Column(VARCHAR(120), unique=True)
    password_hash = Column(VARCHAR(162))
    created_at = Column(DateTime, default=datetime.now)
    is_admin = Column(Boolean, default=False)
