from threading import Thread
import socket
import sys
import os

class Master():
    #def __init__(self, name_server_ip):

    def listen_naming_server(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.listen()
        while True:
            connection, address = sock.accept()
            thread = Thread(target=naming_server, args=(connection, address))
            thread.start()

    def listen_client(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.listen()
        while True:
            connection, address = sock.accept()
            thread = Thread(target=client, args=(connection, address))
            thread.start()

    def client(self, connection, address):
        print("Receiving a file from client with adress:", address)
        filename_size = int.from_bytes(connection.recv(1), 'big') #receive filename size
        filename = (connection.recv(filename_size)).decode() #receive filename


if __name__ == "__main__":
    name_server_ip = "128.0.0.1"
    master = Master()
    naming_listen_thread = Thread(target=master.listen_naming_server, args=(9000,))
    naming_listen_thread.start()
    client_listen_thread = Thread(target=master.listen_client, args=(9001,))
    client_listen_thread.start()
