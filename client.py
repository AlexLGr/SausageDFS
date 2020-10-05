import os
import sys
import requests

working_directory = "/"
# TODO: change master address to the real thing
MASTER = os.getenv("MASTER", "http://localhost:3030/")


def fidelity(args, amount):
    if len(args) != amount:
        print(f"Wrong number of arguments: expected {amount - 1}, got {len(args) - 1}")
        print("Please use 'help' command to learn more about the usage of each command")
        return 0
    else:
        return 1


def verify_response(resp):
    if resp.status_code // 100 == 2:  # status codes 2xx
        print(resp.content.decode())
        return True
    else:
        print(f"{command}:", resp.content.decode())
        return False


def initialize(*args):
    if not fidelity(args, 3):
        return 0
    global working_directory
    working_directory = args[1]
    password = args[2]
    resp = requests.put(
        os.path.join(
            MASTER, f"init?username={working_directory}&password={password}"
        )
    )
    v = verify_response(resp)
    if v:
        print(f"The file system is successfully initialized")
        return 1
    else:
        return 0


def close_session(*args):
    print("Your session is now closed, to come back please use 'login' command")
    sys.exit(0)


def login(*args):
    if not fidelity(args, 3):
        return 0
    username = args[1]
    password = args[2]
    resp = requests.put(
        os.path.join(
            MASTER, f"login?username={username}&password={password}"
        )
    )
    v = verify_response(resp)
    if v:
        global working_directory
        working_directory = username
        return 1
    else:
        return 0


def move_file(*args):
    return 1


def copy_file(*args):
    return 1


def upload_file(*args):
    return 1


def change_dir(*args):
    return 1


def create_dir(*args):
    return 1


def download_file(*args):
    return 1


def list_dir(*args):
    return 1


def remove_file(*args):
    return 1


def remove_dir(*args):
    return 1


def display_help(*args):
    print(
        "Our system supports the following commands:\n"
        "help                         : get information about available commands\n"
        "init <username> <password>   : initialization of a new file system under specified username\n"
        "login <username>             : continue using your filesystem\n"
        "mv <file> <destination>      : move a file to the new destination\n"
        "cp <file> <target>           : copy the content of the file to the different target file \n"
        "put <file> <destination>     : put a local file to the filesystem at the specified destination\n"
        "cd <destination>             : change current working directory\n"
        "mkdir <directory>            : create a new directory\n"
        "get <file> <destination>     : download a file to a local system\n"
        "ls                           : list contents of the current working directory\n"
        "rm <file>                    : remove a specified file\n"
        "rmd <destination>            : remove a directory\n"
        "exit                         : finish you session")
    return 1


commands = {
    "help": display_help,
    "init": initialize,
    "login": login,
    "exit": close_session,
    "mv": move_file,
    "cp": copy_file,
    "put": upload_file,
    "cd": change_dir,
    "mkdir": create_dir,
    "get": download_file,
    "ls": list_dir,
    "rm": remove_file,
    "rmd": remove_dir
}

if __name__ == "__main__":
    print("Client is running")
    print("You can enter a command (type help to view commands and their descriptions)")
    while True:
        command = input().split()
        if len(command) == 0:
            continue
        try:
            commands[command[0]](*command)
        except KeyError:
            print(f"No such command '{command[0]}', please try again")
        except Exception:
            print("Command failed, please try again")
