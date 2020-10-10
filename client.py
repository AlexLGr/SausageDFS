import os
import sys
import requests
from os.path import isabs, join, normpath

working_directory = ""
# TODO: change master address to the real thing
MASTER = os.getenv("MASTER", "http://localhost:3030/")
user = ""
password = ""
secret_key = "-1"


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
    password = args[2]
    resp = requests.put(
        os.path.join(
            MASTER, f"init?username={args[1]}&password={password}"
        )
    )
    v = verify_response(resp)
    if v:
        return 1
    else:
        return 0


def close_session(*args):
    if not fidelity(args, 1):
        return 0
    resp = requests.delete(
        os.path.join(
            MASTER, f"logout?key={secret_key}"
        )
    )
    v = verify_response(resp)
    if v:
        sys.exit(0)


def login(*args):
    if not fidelity(args, 3):
        return 0
    username = args[1]
    ps = args[2]
    resp = requests.put(
        os.path.join(
            MASTER, f"login?username={username}&password={ps}"
        )
    )
    v = verify_response(resp)
    if v:
        global secret_key
        secret_key = resp.content.decode()
        return 1
    else:
        return 0


def upload_file(*args):
    if not fidelity(args, 3):
        return 0
    filepath = args[1]
    destination = args[2]
    try:
        file = open(filepath, "rb").read()
    except OSError as e:
        print(e)
        return 0
    if isabs(destination):
        destination = normpath(destination)
    else:
        destination = normpath(join(working_directory, destination))
    filename = os.path.basename(filepath)
    path = join(destination, filename)
    resp = requests.post(os.path.join(MASTER, f"upload?filename={path}"))
    v = verify_response(resp)
    if v:
        response = resp.json()
        datanodes = response["nodes"]
        for node in datanodes:
            resp = requests.put(join(node, f'upload?filename={path}'), data=file)
            v = verify_response(resp)
            if v:
                return 1
            else:
                return 0
        return 1
    else:
        return 0


def move_file(*args):
    if not fidelity(args, 3):
        return 0
    file = args[1]
    present = requests.post(os.path.join(MASTER, f"cp?name={file}"))
    destination = args[2]
    tokens = destination.split("/")
    dest_dir = ' '.join(map(lambda x: '/' + str(x), tokens))
    valid_destination = requests.post(os.path.join(MASTER, f"cd?name={dest_dir}"))
    if present and valid_destination:
        resp = requests.put(os.path.join(MASTER, f"mv?source={file}"
                                                 f"destination={dest_dir}"))
        verify_response(resp)
    return 1


def copy_file(*args):
    if not fidelity(args, 3):
        return 0
    file = args[1]
    present = requests.post(os.path.join(MASTER, f"cp?name={file}"))
    target = args[2]
    tokens = target.split("/")
    dest_dir = ' '.join(map(lambda x: '/' + str(x), tokens))
    valid_destination = requests.post(os.path.join(MASTER, f"cd?name={dest_dir}"))
    if present and valid_destination:
        resp = requests.put(os.path.join(MASTER, f"cp?source={file}"
                                                 f"target={target}"))
        verify_response(resp)
    return 1


def change_dir(*args):
    if not fidelity(args, 2):
        return 0
    path = args[1]
    global working_directory
    if isabs(path):
        path = normpath(path)
    else:
        path = normpath(join(working_directory, path))
    resp = requests.post(os.path.join(MASTER, f"cd?name={path}"))
    v = verify_response(resp)
    if v:
        working_directory = path
    return 1


def create_dir(*args):
    if not fidelity(args, 2):
        return 0
    path = args[1]
    resp = requests.put(os.path.join(MASTER, f"mkdir?current_dir={working_directory}"
                                             f"&folder_name={path}"
                                             f"&key={secret_key}"))
    v = verify_response(resp)
    if v:
        return 1


def download_file(*args):
    if not fidelity(args, 2):
        return 0
    path = args[1]
    resp = requests.post(os.path.join(MASTER, f"download?filename={path}"))
    if verify_response(resp):
        response = resp.json()
        datanode = response["nodes"]
        resp = requests.post(os.path.join(datanode, f"download?filename={path}"))
        verify_response(resp)
    return 1


def list_dir(*args):
    if not fidelity(args, 2):
        return 0
    global working_directory
    resp = requests.post(os.path.join(MASTER, f"ls?name={working_directory}"))
    response = resp.json()
    contents = response["content"]
    for thing in contents:
        print(thing)
    return 1


def remove_file(*args):
    if not fidelity(args, 2):
        return 0
    file = args[1]
    resp = requests.put(os.path.join(MASTER, f"remove_file?name={file}"))
    verify_response(resp)
    return 1


def remove_dir(*args):
    if not fidelity(args, 2):
        return 0
    dir = args[1]
    resp = requests.put(os.path.join(MASTER, f"remove_dir?name={dir}"))
    verify_response(resp)
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
        "get <file>                   : download a file to a local system\n"
        "ls                           : list contents of the current working directory\n"
        "rm <file>                    : remove a specified file\n"
        "rmd <destination>            : remove a directory\n"
        "exit                         : finish you session")
    return 1


commands = {
    "help": display_help, #DONE
    "init": initialize, #DONE
    "login": login, #DONE
    "exit": close_session, #DONE
    "mv": move_file,
    "cp": copy_file,
    "put": upload_file,
    "cd": change_dir,
    "mkdir": create_dir, #DONE
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