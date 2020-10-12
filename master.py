from flask import Flask, Response
from flask import jsonify, Response, request, session
from datetime import datetime
import random
import requests
import uuid
import socket
from FsTree import FsTree

app = Flask(__name__)
PORT = 3030
DEBUG = True
users = {}
sessions = {}
# For storage servers pool
storage_servers = ['1', '2', '3']

fs = FsTree('')
fs.set_replicas(storage_servers)


def check_session(key):
    if key in sessions:
        if (sessions[key][1] - datetime.now()).total_seconds() < 600:
            return True
        else:
            sessions.pop(key)
            return False
    else:
        return False


@app.route("/login", methods=["PUT"])
def login():
    username = request.args["username"]
    password = request.args["password"]
    current_users = list(users.keys())
    if username in current_users:
        if users[username] == password:
            key = str(uuid.uuid1())
            sessions[key] = [username, datetime.now()]
            return Response(f"{key}", status=200)
        else:
            return Response(f"Wrong password", status=400)
    else:
        return Response(f"User '{username}' does not exist", status=400)


@app.route("/logout", methods=["DELETE"])
def logout():
    key = request.args["key"]
    if check_session(key):
        sessions.pop(key)
        return Response("Your session is now closed, to come back please use 'login' command",
                        status=200)
    else:
        return Response("No session found for your account, please log in", status=400)


@app.route("/init", methods=["PUT"])
def init():
    username = request.args["username"]
    password = request.args["password"]
    current_users = list(users.keys())
    if username in current_users:
        return Response(f"User '{username}' already exists", status=400)
    else:
        users[username] = password
        user_folder = FsTree(username)
        fs.add_child(user_folder)
        for server in user_folder.replicas:
            port = 9000
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server, port))

            command = "mkdir"

            sock.send(len(command).to_bytes(1, 'big'))
            sock.send(command.encode())
            current_dir = ''
            sock.send(len(current_dir).to_bytes(1, 'big'))
            sock.send(current_dir.encode())
            folder_name = username
            sock.send(len(folder_name).to_bytes(1, 'big'))
            sock.send(folder_name.encode())

        return Response(f"User '{username}' was successfully created", status=200)


@app.route("/mkdir", methods=["PUT"])
def mkdir():
    key = request.args["key"]
    if check_session(key):
        current_dir = sessions[key][0] + '/' + request.args["current_dir"]
        folder_name = request.args["folder_name"]
        temp = fs.get_child(current_dir)
        if temp:
            temp.add_child(FsTree(folder_name))
            for server in temp.replicas:
                port = 9000
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server, port))

                command = "mkdir"

                sock.send(len(command).to_bytes(1, 'big'))
                sock.send(command.encode())

                sock.send(len(current_dir).to_bytes(1, 'big'))
                sock.send(current_dir.encode())

                sock.send(len(folder_name).to_bytes(1, 'big'))
                sock.send(folder_name.encode())

            return Response("Directory successfully created", status=200)
        else:
            return Response("Error in creating directory, please verify your input", status=400)
    else:
        return Response("Operation unavailable, please log in first", status=400)


@app.route("/ls", methods=["POST"])
def ls():
    key = request.args["key"]
    dir_name = request.args["name"]

    if check_session(key):
        path = sessions[key][0] + '/' + dir_name
        temp = fs.get_child(path)
        if temp:
            return Response({
                'content': temp.list_children()
            }, status=200)
        else:
            return Response("Wrong directory", status=404)
    return Response("No session found for your account, please log in", status=400)


@app.route("/cd", methods=["POST"])
def change_dir():
    key = request.args["key"]
    dir_name = request.args["name"]

    if check_session(key):
        path = sessions[key][0] + '/' + dir_name
        if fs.get_child(path):
            return Response("Directory was changed", status=200)
        else:
            return Response("No such directory was found", status=404)
    return Response("No session found for your account, please log in", status=400)


@app.route("/mv", methods=["PUT"])
def move():
    key = request.args["key"]

    if check_session(key):
        old_path = sessions[key][0] + '/' + request.args['source']
        new_path = sessions[key][0] + '/' + request.args['destination']
        filename = old_path.split('/')[-1]
        old_fs = fs.get_child(old_path)
        new_fs = fs.get_child(new_path)

        if old_fs and new_fs:
            old_fs.sync()

            new_fs.add_child(FsTree(filename))
            for server in new_fs.replicas:
                port = 9000
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server, port))

                command = "mv"

                sock.send(len(command).to_bytes(1, 'big'))
                sock.send(command.encode())

                sock.send(len(old_path).to_bytes(1, 'big'))
                sock.send(old_path.encode())

                sock.send(len(new_path).to_bytes(1, 'big'))
                sock.send(new_path.encode())

            new_fs.get_child(filename).set_sync(True)

            old_parent = old_path.split('/')[:-1]
            fs.get_child(old_parent).remove_child(filename)
    else:
        Response("No session found for your account, please log in", status=400)


@app.route("/cp", methods=["PUT"])
def copy():
    key = request.args["key"]

    if check_session(key):
        old_path = sessions[key][0] + '/' + request.args['source']
        new_path = sessions[key][0] + '/' + request.args['target']
        filename = old_path.split('/')[-1]
        old_fs = fs.get_child(old_path)
        new_fs = fs.get_child(new_path)
        if old_fs and new_fs:
            old_fs.sync()
            new_fs.add_child(FsTree(filename))

            if old_fs.sync:
                server = new_fs.get_child(filename).address
            else:
                server = old_fs.address
                new_fs.get_child(filename).set_address(server)

            port = 9000
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server, port))

            command = "cp"

            sock.send(len(command).to_bytes(1, 'big'))
            sock.send(command.encode())

            sock.send(len(old_path).to_bytes(1, 'big'))
            sock.send(old_path.encode())

            sock.send(len(new_path).to_bytes(1, 'big'))
            sock.send(new_path.encode())

            new_fs.get_child(filename).sync()
    else:
        Response("No session found for your account, please log in", status=400)


@app.route("/download", methods=["POST"])
def download():
    path = request.args["name"]
    key = request.args["key"]

    if check_session(key):
        path = sessions[key][0] + '/' + path
        temp = fs.get_child(path)
        if temp:
            if temp.sync:
                return Response({
                    'nodes': random.choice(temp.replicas)
                }, status=200)

            else:
                return Response({
                    'nodes': temp.address
                }, status=200)
        else:
            return Response("No such file was found", status=404)
    return Response("No session found for your account, please log in", status=400)


@app.route("/upload", methods=["POST"])
def upload():
    # получишь файл в переменной filename, отправишь лист IP серверов готовых принять файл в json
    key = request.args["key"]

    if check_session(key):
        path = sessions[key][0] + '/' + request.args["path"]
        file = request.args["filename"]
        temp = fs.get_child(path)
        if temp:
            temp.add_child(FsTree(file))

            return Response({
                'nodes': temp.get_child(file).address
            }, status=200)
    else:
        return Response("Operation unavailable, please log in first", status=400)


@app.route("/remove_file", methods=["PUT"])
def remove_file():
    key = request.args["key"]
    if check_session(key):
        file_path = sessions[key][0] + '/' + request.args["name"]
        temp = fs.get_child(file_path)
        if temp:
            folders = file_path.split('/')

            path = '/'.join(folders[:-1])
            filename = folders[-1]

            for server in temp.replicas:
                port = 9000
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server, port))

                command = "rm"

                sock.send(len(command).to_bytes(1, 'big'))
                sock.send(command.encode())

                sock.send(len(path).to_bytes(1, 'big'))
                sock.send(path.encode())

                sock.send(len(filename).to_bytes(1, 'big'))
                sock.send(filename.encode())

            fs.get_child(path).remove_child(filename)

            return Response("File was successfully deleted", status=200)
        else:
            return Response("File was not found", status=404)
    else:
        return Response("Operation unavailable, please log in first", status=400)


@app.route("/remove_dir", methods=["PUT"])
def remove_dir():
    key = request.args["key"]
    if check_session(key):
        folderpath = sessions[key][0] + '/' + request.args["name"]
        temp = fs.get_child(folderpath)
        if temp:
            folders = folderpath.split('/')

            path = '/'.join(folders[:-1])
            foldername = folders[-1]

            for server in temp.replicas:
                port = 9000
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server, port))

                command = "rmd"

                sock.send(len(command).to_bytes(1, 'big'))
                sock.send(command.encode())

                sock.send(len(folderpath).to_bytes(1, 'big'))
                sock.send(folderpath.encode())

            fs.get_child(path).remove_child(foldername)

            return Response("Directory was successfully deleted", status=200)
        else:
            return Response("Directory was not found", status=404)
    else:
        return Response("Operation unavailable, please log in first", status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
