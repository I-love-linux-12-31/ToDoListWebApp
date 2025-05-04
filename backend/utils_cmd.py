#!/bin/env python3
import os
import sys
from utils.add_user import add_user, add_user_not_interactive


def parse_args(args):
    result = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--"):
            key = args[i][2:]
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]
                i += 1
            else:
                value = None  # Если значение не указано
            result[key] = value
        i += 1
    return result


def help_dialog():
    text = """
    Available commands:
 exit - exit the program
 help - show this message
 add_user - add a new user
    """
    print(text)

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        kwargs = parse_args(sys.argv[2:])
        match cmd:
            case "add_user":
                add_user_not_interactive(**kwargs)
            case _:
                print("Not supported in not interactive mode!")
                sys.exit(1)
        sys.exit(0)

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


if __name__ == "__main__":
    if sys.version_info[1] >= 13: # 3.13 +
        print(
            "Warning! Non interactive script may not work in this python version"
            "(especially in free-thread mode and 3.14)",
        )
    from db import global_init
    if os.environ.get("DOTENV", False):
        from dotenv import load_dotenv
        load_dotenv()
    global_init()
    main()
