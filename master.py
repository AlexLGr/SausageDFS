from flask import Flask, Response
from flask import jsonify, Response, request, session
import random
import requests
import uuid

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
        self.address = ""
        self.replicas = []
        self.children = []

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
        return True

    def add_replicas(self, replica_address: str):
        if replica_address in self.replicas:
            return False
        else:
            self.replicas.append(replica_address)
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


fs = FsTree('.')


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
        for server in ss:
            user_folder.add_replicas(server)
        return Response(f"User '{username}' was successfully created", status=200)


@app.route("/login", methods=["PUT"])
def login():
    username = request.args["username"]
    password = request.args["password"]
    current_users = list(users.keys())
    if username in current_users:
        if users[username] == password:
            key = uuid.uuid1()
            sessions[key] = username
            return Response(f"{key}", status=200)
        else:
            return Response(f"Wrong password", status=400)
    else:
        return Response(f"User '{username}' does not exist", status=400)


@app.route("/mkdir", methods=["PUT"])
def mkdir():
    secret_key = int(request.args["key"])
    current_keys = sessions.keys()
    if secret_key in current_keys:
        current_dir = sessions[secret_key] + '/' + request.args["current_dir"]
        folder_name = request.args["folder_name"]
        temp = fs.get_child(current_dir)
        if temp:
            temp.add_child(FsTree(folder_name))
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
