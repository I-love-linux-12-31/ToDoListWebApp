import os

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return

    if os.environ.get("DB_TYPE", "???").lower() in ("sqlite", "sqlite3", "filedb"):
        file_path = os.environ.get("DB_FILE_PATH", "/tmp/db.sqlite3")
        conn_str = f"sqlite:///{file_path}?check_same_thread=False"
    else:
        conn_str = f'{os.environ.get("DB_TYPE", "mariadb+pymysql")}://{os.environ.get("DB_USER", "user")}:{os.environ.get("DB_PASSWORD", "Password_123")}@{os.environ.get("DB_SERVER", "127.0.0.1")}/{os.environ.get("DB", "ToDoListWebApp")}' # check_same_thread=False&
        if os.environ.get("DB_TYPE", "mariadb+pymysql") == "mariadb+pymysql":
            conn_str += f"?charset=utf8mb4&"
    print(f"Connecting to DB: {conn_str}".replace(os.environ.get("DB_PASSWORD", "Password_123"), "<PASSWORD>"))

    engine = sa.create_engine(conn_str, echo=False, connect_args={'connect_timeout': 60}, pool_size=10, max_overflow=20)
    __factory = orm.sessionmaker(bind=engine)
    from ORM import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
