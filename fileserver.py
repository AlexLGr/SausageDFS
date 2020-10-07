from threading import Thread
import socket
import sys
import os

class Master():
    #def init(self, name_server_ip):
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
            thread = Thread(target=self.client, args=(connection, address))
            thread.start()

    def client(self, connection, address):
        print("Speaking with client with address:", address)
        command_size = int.from_bytes(connection.recv(1), 'big') #receive command size
        command = (connection.recv(command_size)).decode() #receive command
        print("Recieved command:", command)
        if(command == "put"):
            self.put(connection, address)
        elif(command == "mkdir"):
            self.mkdir(connection, address)
        return

    def put(self, connection, address):
        virtual_path_size = int.from_bytes(connection.recv(1), 'big') #receive virtual path size
        virtual_path = (connection.recv(virtual_path_size)).decode() #receive virtual path

        print("Recieved path:", virtual_path)

        filename_size = int.from_bytes(connection.recv(1), 'big') #receive filename size
        filename = (connection.recv(filename_size)).decode() #receive filename

        print("Recieved name of file:", filename)
        #os.system(f'touch {virtual_path}/{filename}')
        file = open(f'{virtual_path}{filename}', "wb")
        while True:
            data = connection.recv(1024)
            if not data:
                break
            file.write(data)
        print("Received file with name:", filename)
        print(f'put {filename} to /{virtual_path}/')
        file.close()
        return

    def mkdir(self, connection, address):
        virtual_path_size = int.from_bytes(connection.recv(1), 'big') #receive virtual path size
        virtual_path = (connection.recv(virtual_path_size)).decode() #receive virtual path
        print("Recieved path:", virtual_path)
        dirname_size = int.from_bytes(connection.recv(1), 'big') #receive filename size
        dirname = (connection.recv(dirname_size)).decode() #receive filename
        print("Recieved dirname of file:", dirname)

        os.mkdir(f"{virtual_path}{dirname}")
        return

    def replicate(replica_ip):

        return True

    def virtual_path_to_real(path):
        return path

if name == "main":
    name_server_ip = "localhost"
    master = Master()
    naming_listen_thread = Thread(target=master.listen_naming_server, args=(9000,))
    naming_listen_thread.start()
    client_listen_thread = Thread(target=master.listen_client, args=(9090,))
    client_listen_thread.start()
