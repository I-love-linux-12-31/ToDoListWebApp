from werkzeug.security import generate_password_hash

def ask_boolean_question(question, __another_try=False) -> bool:
    if __another_try:
        print("Incorrect input. Choose Y or N.")
    print(question, "Y/N? ")
    response = input().upper()
    if response == 'Y' or response == 'YES':
        return True
    elif response == 'N' or response == 'NO':
        return False
    return ask_boolean_question(question, __another_try=True)

def ask_new_password() -> str:
    passwd = input("New password: ")
    confirm = input("Confirm password: ")
    if confirm != passwd:
        print("Passwords do not match.")
        return ask_new_password()
    return generate_password_hash(passwd)
