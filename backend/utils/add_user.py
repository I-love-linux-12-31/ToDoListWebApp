from datetime import datetime

from ORM.users import User
from db import create_session

from .common import ask_new_password, ask_boolean_question

def add_user():
    print(">> Add user")
    username = input("Username: ")
    email = input("Email: ")
    created_at = datetime.now()
    is_admin = ask_boolean_question("Is admin?")
    password = ask_new_password()

    try:
        with create_session() as session:
            user = User()
            user.username = username
            user.email = email
            user.created_at = created_at
            user.is_admin = is_admin
            user.password_hash = password
            session.add(user)
            session.commit()
    except Exception as e:
        print("Failed to add user.")
        print(F"Error: {e.__class__.__name__}: {e}")
        return
    print("Added new user!")


def main():
    add_user()

if __name__ == '__main__':
    main()
