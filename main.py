from threading import Thread
import socket
import sys
import os
import commands
import replication

def listen_naming_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen()
    while True:
        connection, address = sock.accept()
        thread = Thread(target=naming_server, args=(connection, address))
        thread.start()

def listen_client(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen()
    while True:
        connection, address = sock.accept()
        thread = Thread(target=client, args=(connection, address))
        thread.start()

def listen_replica(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen()
    while True:
        connection, address = sock.accept()
        thread = Thread(target=replication.receive_replica, args=(connection, address))
        thread.start()

def client(connection, address):
    print("Speaking with client with address:", address)
    command_size = int.from_bytes(connection.recv(1), 'big') #receive command size
    command = (connection.recv(command_size)).decode() #receive command
    print("Recieved command:", command)
    if(command == "put"):
        commands.put(connection, address)
    elif(command == "mkdir"):
        commands.mkdir(connection, address)
    elif(command == "replicate"):
        replication.replicate(connection, address)
    return

def virtual_path_to_real(path):
    return path

if __name__ == "__main__":
    name_server_ip = "localhost"
    naming_listen_thread = Thread(target=listen_naming_server, args=(10000,))
    naming_listen_thread.start()
    client_listen_thread = Thread(target=listen_client, args=(10001,))
    client_listen_thread.start()
    replica_listen_thread = Thread(target=listen_replica, args=(10002,))
    replica_listen_thread.start()
