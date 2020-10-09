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

    os.system(f'mkdir {virtual_path}{dirname}')
    return

def mv(connection, address):
    from_path_size = int.from_bytes(connection.recv(1), 'big') #receive virtual path size
    from_path = (connection.recv(from_path_size)).decode() #receive virtual path
    print("Recieved from path:", from_path)

    to_path_size = int.from_bytes(connection.recv(1), 'big') #receive virtual path size
    to_path = (connection.recv(to_path_size)).decode() #receive virtual path
    print("Recieved to path:", to_path)
    os.system(f'mv {from_path} {to_path}')
    #os.replace(from_path, to_path)
    return

def cp(connection, address):
    from_path_size = int.from_bytes(connection.recv(1), 'big') #receive virtual path size
    from_path = (connection.recv(from_path_size)).decode() #receive virtual path
    print("Recieved from path:", from_path)

    to_path_size = int.from_bytes(connection.recv(1), 'big') #receive virtual path size
    to_path = (connection.recv(to_path_size)).decode() #receive virtual path
    print("Recieved to path:", to_path)
    os.system(f'cp {from_path} {to_path}')
    return


### GET NOT WORKING!
def get(connection, address):
    virtual_path_size = int.from_bytes(connection.recv(1), 'big') #receive virtual path size
    virtual_path = (connection.recv(virtual_path_size)).decode() #receive virtual path
    print("Recieved path:", virtual_path)

    if os.path.isfile(virtual_path):
        file_size = os.path.getsize(virtual_path)  #size of file
        sent = 0
        file = open(virtual_path, "rb")
        while True:
            print(f"{sent} of {file_size} bytes sent - {sent * 100 / file_size :.2f}% done")
            buf = file.read(1024) #send data of file
            if not buf:
                break
            sock.sendall(buf)
            sent += len(buf)
        print("Finished!")
    else:
        print("Failed.")
    return
