import os
import sys
import requests
from os.path import isabs, join, normpath
import socket

working_directory = ""
# TODO: change master address to the real thing
MASTER = os.getenv("MASTER", "http://localhost:3030/")
user = ""
password = ""
secret_key = "-1"
SEPARATOR = "<SEPARATOR>"


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
        global secret_key, user
        user = username
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
    filename = os.path.basename(filepath)
    resp = requests.post(os.path.join(MASTER, f"upload?filename={filename}"
                                              f"&path={destination}"
                                              f"&key={secret_key}"))
    response = resp.json()
    datanodes = response["nodes"]
    print(datanodes)
    global user
    destination = user + "/" + destination
    for node in datanodes:
        port = 10001
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((node, port))

        sock.sendall(len("put").to_bytes(1, 'big')) #sending command
        sock.sendall(str("put").encode())


        sock.sendall(len(destination).to_bytes(1, 'big')) #sending path
        sock.sendall(str(destination).encode())

        sock.sendall(len(filename).to_bytes(1, 'big')) #sending filename
        sock.sendall(str(filename).encode())


        if os.path.isfile(filename):
            file_size = os.path.getsize(filename)  #size of file
            sent = 0
            file = open(filename, "rb")
            while True:
                print(f"{sent} of {file_size} bytes sent - {sent * 100 / file_size :.2f}% done")
                buf = file.read(1024) #send data of file
                if not buf:
                    break
                sock.sendall(buf)
                sent += len(buf)
            print("Finished!")
        else:
            print("Failed.")
    return 0

def move_file(*args):
    if not fidelity(args, 3):
        return 0
    file = args[1]
    present = requests.post(os.path.join(MASTER, f"cd?name={file}"
                                                 f"&key={secret_key}"))
    destination = args[2]
    tokens = destination.split("/")
    dest_dir = ' '.join(map(lambda x: '/' + str(x), tokens))
    valid_destination = requests.post(os.path.join(MASTER, f"cd?name={dest_dir}"
                                                           f"&key={secret_key}"))
    if present and valid_destination:
        resp = requests.put(os.path.join(MASTER, f"mv?source={file}"
                                                 f"&destination={dest_dir}"
                                                 f"&key={secret_key}"))
        verify_response(resp)
    return 1


def copy_file(*args):
    if not fidelity(args, 3):
        return 0
    file = args[1]
    present = requests.post(os.path.join(MASTER, f"cd?name={file}"
                                                 f"&key={secret_key}"))
    target = args[2]
    tokens = target.split("/")
    dest_dir = ' '.join(map(lambda x: '/' + str(x), tokens))
    valid_destination = requests.post(os.path.join(MASTER, f"cd?name={dest_dir}"
                                                           f"&key={secret_key}"))
    if present and valid_destination:
        resp = requests.put(os.path.join(MASTER, f"cp?source={file}"
                                                 f"target={target}"
                                                 f"&key={secret_key}"))
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
    resp = requests.post(os.path.join(MASTER, f"cd?name={path}"
                                              f"&key={secret_key}"))
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
    resp = requests.post(os.path.join(MASTER, f"download?filename={path}"
                                              f"&key={secret_key}"))
    response = resp.json()
    datanode = response["nodes"]
    print(datanode)
    global user
    path = user + "/" + path
    port = 10001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((datanode, port))

    sock.sendall(len("get").to_bytes(1, 'big')) #sending command
    sock.sendall(str("get").encode())
    sock.sendall(len(path).to_bytes(1, 'big')) #sending path
    sock.sendall(str(path).encode())

    localpath = path.split("/")[-1]
    print(localpath)
    file = open(f'{localpath}', "wb")
    print("жив2")
    while True:
        data = sock.recv(1024)
        if not data:
            print("break")
            break
        file.write(data)
    file.close()
    sock.close()
    print("Received file with name:", localpath)


def list_dir(*args):
    if not fidelity(args, 1):
        return 0
    global working_directory
    resp = requests.post(os.path.join(MASTER, f"ls?name={working_directory}"
                                              f"&key={secret_key}"))
    response = resp.json()
    contents = response["content"]
    for thing in contents:
        print(thing)
    return 1


def remove_file(*args):
    if not fidelity(args, 2):
        return 0
    file = args[1]
    resp = requests.put(os.path.join(MASTER, f"remove_file?name={file}"
                                             f"&key={secret_key}"))
    verify_response(resp)
    return 1


def remove_dir(*args):
    if not fidelity(args, 2):
        return 0
    dir = args[1]
    resp = requests.put(os.path.join(MASTER, f"remove_dir?name={dir}"
                                             f"&key={secret_key}"))
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
        "touch <filename>             : create a new file with the name filename\n"
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
    "rmd": remove_dir,
    "touch": create_dir
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
