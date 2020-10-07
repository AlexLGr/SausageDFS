from threading import Thread
import socket
import sys
import os

def put(connection, address):
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

def mkdir(connection, address):
    virtual_path_size = int.from_bytes(connection.recv(1), 'big') #receive virtual path size
    virtual_path = (connection.recv(virtual_path_size)).decode() #receive virtual path
    print("Recieved path:", virtual_path)
    dirname_size = int.from_bytes(connection.recv(1), 'big') #receive filename size
    dirname = (connection.recv(dirname_size)).decode() #receive filename
    print("Recieved dirname of file:", dirname)

    os.mkdir(f"{virtual_path}{dirname}")
    return
