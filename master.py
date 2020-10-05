from flask import Flask, Response
from flask import jsonify, Response, request
import random
import requests

app = Flask(__name__)
PORT = 3030
DEBUG = True
users = {}
# For storage servers pool
storage_servers = []


class FsTree:
    def __init__(self, name: str):
        self.name = name
        self.address = ""
        self.replicas = []
        self.childs = []

    def add_child(self, child):
        if child not in self.childs:
            self.childs.append(child)
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

        for child in self.childs:
            if child.name == folders[0]:
                return child.get_child('/'.join(folders[1:]))

        return False

    def list_childs(self):
        for child in self.childs:
            print(child.name)


fs = FsTree('.')


@app.route("/init", methods=["PUT"])
def init():
    username = request.args["username"]
    password = request.args["password"]
    current_users = list(users.keys())
    if username in current_users:
        return Response(f"User '{username}' already exists")
    else:
        users[username] = password
        user_folder = FsTree(username)
        fs.add_child(user_folder)
        ss = random.choices(storage_servers, k = 3)
        for server in ss:
            user_folder.add_replicas(server)
        return Response(f"User '{username}' was successfully created")


@app.route("/login", methods=["PUT"])
def login():
    username = request.args["username"]
    password = request.args["password"]
    current_users = list(users.keys())
    if username in current_users:
        if users[username] == password:
            return Response(f"Welcome back {username}")
        else:
            return Response(f"Wrong password")
    else:
        return Response(f"User '{username}' does not exist")


@app.route("/mkdir", methods=["PUT"])
def mkdir():
    current_dir = request.args["current_dir"]
    folder_name = request.args["folder_name"]

    temp = fs.get_child(current_dir)
    if temp:
        temp.add_child(FsTree(folder_name))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
