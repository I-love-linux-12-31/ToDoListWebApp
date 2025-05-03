from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum, CHAR
import enum

from db import SqlAlchemyBase

class TokensAccessLevels(enum.Enum):
    """
    Token access levels enum.
    """

    READONLY = 0
    READ_UPDATE = 1
    READ_CREATE = 2
    EVERYTHING_USER = 3
    EVERYTHING_ADMIN = 4

    @staticmethod
    def level_by_id(level_id):
        match level_id:
            case 0:
                return TokensAccessLevels.READONLY
            case 1:
                return TokensAccessLevels.READ_UPDATE
            case 2:
                return TokensAccessLevels.READ_CREATE
            case 3:
                return TokensAccessLevels.EVERYTHING_USER
            case 4:
                return TokensAccessLevels.EVERYTHING_ADMIN
            case _:
                return TokensAccessLevels.READONLY

    @staticmethod
    def id_by_level(level):
        match level:
            case TokensAccessLevels.READONLY:
                return 0
            case TokensAccessLevels.READ_UPDATE:
                return 1
            case TokensAccessLevels.READ_CREATE:
                return 2
            case TokensAccessLevels.EVERYTHING_USER:
                return 3
            case TokensAccessLevels.EVERYTHING_ADMIN:
                return 4
        return None

    def __gt__(self, other):
        return self.id_by_level(self) > other.id_by_level(other)

    def __lt__(self, other):
        return self.id_by_level(self) < other.id_by_level(other)


class AuthToken(SqlAlchemyBase):
    """
    Auth token class.
    """

    __tablename__ = "auth_tokens"
    id = Column(CHAR(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    valid_until = Column(DateTime)
    access_level = Column(Enum(TokensAccessLevels), default=TokensAccessLevels.READONLY)

    def __str__(self):
        return f"Auth token {self.id} owned by {self.user_id}. Valid until {self.valid_until}."

    def serialize_from_object(self):
        return {
            "id": self.id,
            "access_level": self.access_level.value,
            "valid_until": self.valid_until.isoformat(),
            "user_id": self.user_id,
        }
