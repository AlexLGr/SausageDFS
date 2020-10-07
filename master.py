from flask import Flask, Response
from flask import jsonify, Response, request, session
from datetime import datetime
import random
import requests
import uuid
import socket

app = Flask(__name__)
PORT = 3030
DEBUG = True
users = {}
sessions = {}
# For storage servers pool
storage_servers = ['1', '2', '3']


class FsTree:
    def __init__(self, name: str):
        self.name = name
        self.path = ""
        self.address = ""
        self.replicas = []
        self.children = []
        self.sync = False

    def set_path(self, path: str):
        self.path = path

    def add_child(self, child):
        if child not in self.children:
            child.set_path(self.path + child.name)
            self.children.append(child)
        return True

    def set_replicas(self, replicas: str):
        self.replicas = replicas
        for child in self.children:
            child.set_replicas(replicas)
        self.sync = False
        return True

    def set_address(self, address: str):
        self.address = address

    def get_child(self, path: str):
        if path == '':
            return self

        folders = path.split('/')

        for child in self.children:
            if child.name == folders[0]:
                return child.get_child('/'.join(folders[1:]))

        return False

    def list_children(self):
        for child in self.children:
            print(child.name)

    def sync(self):
        if not self.sync:
            port = 9000
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.address, port))

            command = "sync"

            sock.send(len(command).to_bytes(1, 'big'))
            sock.send(command.encode())

            sock.send(len(self.path).to_bytes(1, 'big'))
            sock.send(self.path.encode())

            sock.send(len(self.replicas).to_bytes(1, 'big'))

            for replica in self.replicas:
                if replica != self.address:
                    sock.send(replica.encode())


fs = FsTree('')


def check_session(key):
    if key in sessions:
        if (sessions[key][1] - datetime.now()).total_seconds() < 600:
            return True
        else:
            sessions.pop(key)
            return False
    else:
        return False


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
        ss = random.choices(storage_servers, k=3)
        user_folder.set_replicas(ss)
        return Response(f"User '{username}' was successfully created", status=200)


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


@app.route("/logout", methods=["DELETE"])
def logout():
    key = int(request.args["key"])
    current_keys = sessions.keys()
    if key in current_keys:
        sessions.pop(key)
        return Response("Your session is now closed, to come back please use 'login' command",
                        status=200)
    else:
        return Response("No session found for your account, please log in", status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)

