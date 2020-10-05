from flask import Flask, Response
from flask import jsonify, Response, request
import requests

app = Flask(__name__)
PORT = 3030
DEBUG = True
users = {}


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
