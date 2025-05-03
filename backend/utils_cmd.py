#!/bin/env python3
import os
from utils.add_user import add_user


def help_dialog():
    text = """
    Available commands:
 exit - exit the program
 help - show this message    
 add_user - add a new user
    
    """
    print(text)

def main():
    print("Welcome to debug console. use 'help' to see available commands.")
    while True:
        cmd = input("> ")
        match cmd:
            case "exit":
                break
            case "help":
                help_dialog()
            case "add_user":
                add_user()
            case _:
                print("Unknown command.")
    print()
    print("Goodbye!")


if __name__ == '__main__':
    from db import global_init
    if os.environ.get("DOTENV", False):
        from dotenv import load_dotenv
        load_dotenv()

    global_init()
    main()
