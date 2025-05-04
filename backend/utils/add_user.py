from datetime import datetime, UTC

from ORM.users import User
from db import create_session
from werkzeug.security import generate_password_hash

from .common import ask_new_password, ask_boolean_question


def add_user_not_interactive(username, password, email=None, is_admin=False, created_at=None, **kwargs):
    # print("Adding user (not interactive)", username, password, email, is_admin, created_at)
    if "admin" in kwargs and str(kwargs["admin"]).upper() in ("TRUE", "YES", "1"):
        is_admin = True
    if created_at is None:
        created_at = datetime.now(UTC)
    try:
        with create_session() as session:
            user = User()
            user.username = username
            user.email = email
            user.created_at = created_at
            user.is_admin = is_admin
            user.password_hash = generate_password_hash(password)
            session.add(user)
            session.commit()
            return True
    except Exception as e:
        print("Failed to add user.")
        print(F"Error: {e.__class__.__name__}: {e}")
        return False


def add_user():
    print(">> Add user")
    username = input("Username: ")
    email = input("Email: ")
    created_at = datetime.now()
    is_admin = ask_boolean_question("Is admin?")
    password = ask_new_password()
    if add_user_not_interactive(username, password, email=email, is_admin=is_admin):
        print("Added new user!")


def main():
    add_user()

if __name__ == "__main__":
    main()
