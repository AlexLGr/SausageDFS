from flask import Flask, Response
from flask import jsonify, Response, request
import requests

app = Flask(__name__)
PORT = 3030
DEBUG = True
users = {}

class fstree:
    name = ""
    address = ""
    replicas = []
    childs = []

    def __init__(self, name):
        self.name = name

    def add_child(self, child):
        if child in self.childs:
            return False
        else:
            self.childs.append(child)
            return True

    def add_replicas(self, replica_address):
        if replica_address in self.replicas:
            return False
        else:
            self.replicas.append(replica_address)
            return True

    def set_address(self, address):
        self.address = address


@app.route("/init", methods=["PUT"])
def init():
    username = request.args["username"]
    password = request.args["password"]
    current_users = list(users.keys())
    if username in current_users:
        return Response(f"User '{username}' already exists")
    else:
        users[username] = password
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


@app.route("/login", methods=["PUT"])
def mkdir():
    current_dir = request.args["current_dir"]
    folder_name = request.args["folder_name"]



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)