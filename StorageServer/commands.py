from threading import Thread
import socket
import sys
import os

def put(connection, address):
    path_size = int.from_bytes(connection.recv(1), 'big') #receive  path size
    path = (connection.recv(path_size)).decode() #receive  path
    print("Recieved path:", path)

    filename_size = int.from_bytes(connection.recv(1), 'big') #receive filename size
    filename = (connection.recv(filename_size)).decode() #receive filename
    print("Received file with name:", filename)

    if os.path.exists(absolute_path(path)):
        try:
            file = open(f'{virtual_path}{filename}', "wb")
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                file.write(data)
            print(f'put {filename} to /{virtual_path}/ successful')
            file.close()
            return
        except:
            return f'Unable to put file to {path}'
    else:
        return f'Path {path} is not exist.'

def mkdir(connection, address):
    path_size = int.from_bytes(connection.recv(1), 'big') #receive path size
    path = (connection.recv(path_size)).decode() #receive path
    print("Recieved path:", path)

    dirname_size = int.from_bytes(connection.recv(1), 'big') #receive directory name size
    dirname = (connection.recv(dirname_size)).decode() #receive directory name
    print("Recieved dirname of file:", dirname)

    if os.path.exists(absolute_path(path)):
        try:
            os.system(f'mkdir {path}{dirname}')
            return
        except:
            print(f'Unable to make directory with path {path}')
            return f'Unable to make directory with path {path}'
    else:
        print(f'Path {path} is not exist.')
        return f'Path {path} is not exist.'

def mv(connection, address):
    from_path_size = int.from_bytes(connection.recv(1), 'big') #receive 'to move from' path size
    from_path = (connection.recv(from_path_size)).decode() #receive 'to move from' path
    print("Recieved from path:", from_path)

    to_path_size = int.from_bytes(connection.recv(1), 'big') #receive 'to move to' path size
    to_path = (connection.recv(to_path_size)).decode() #receive 'to move to' path size
    print("Recieved to path:", to_path)

    if os.path.exists(absolute_path(from_path)) and os.path.exists(absolute_path(to_path)):
        try:
            os.system(f'mv {from_path} {to_path}')
            return
        except:
            return f'Unable to move file from {from_path} to {to_path}'
    elif not os.path.exists(from_path) :
        return f'Path {from_path} is not exist.'
    else:
        return f'Path {to_path} is not exist.'

def cp(connection, address):
    from_path_size = int.from_bytes(connection.recv(1), 'big') #receive 'to cp from' path size
    from_path = (connection.recv(from_path_size)).decode() #receive 'to cp from' path
    print("Recieved from path:", from_path)

    to_path_size = int.from_bytes(connection.recv(1), 'big') #receive 'to cp to' path size
    to_path = (connection.recv(to_path_size)).decode() #receive 'to cp to' path
    print("Recieved to path:", to_path)

    if os.path.exists(absolute_path(from_path)) and os.path.exists(absolute_path(to_path)):
        try:
            os.system(f'cp {from_path} {to_path}')
            return
        except:
            return f'Unable to copy file from {from_path} to {to_path}'
    elif not os.path.exists(from_path) :
        return f'Path {from_path} is not exist.'
    else:
        return f'Path {to_path} is not exist.'


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

def rm(connection, address):
    path_size = int.from_bytes(connection.recv(1), 'big') #receive  path size
    path = (connection.recv(path_size)).decode() #receive  path
    print("Recieved path:", path)

    filename_size = int.from_bytes(connection.recv(1), 'big') #receive filename size
    filename = (connection.recv(filename_size)).decode() #receive filename
    print("Received file with name:", filename)

    if os.path.exists(absolute_path(path)):
        try:
            os.system(f'rm {path}{filename}')
            return
        except:
            print(f'Unable to remove file {filename}')
            return f'Unable to remove file {filename}'
    else:
        print(f'Path {path} is not exist.')
        return f'Path {path} is not exist.'

def rmd(connection, address):
    path_size = int.from_bytes(connection.recv(1), 'big') #receive  path size
    path = (connection.recv(path_size)).decode() #receive  path
    print("Recieved path:", path)

    if os.path.exists(absolute_path(path)):
        try:
            os.system(f'rmdir {path}')
            return
        except:
            print(f'Unable to remove {path}')
            return f'Unable to remove file {path}'
    else:
        print(f'Path {path} is not exist.')
        return f'Path {path} is not exist.'

def absolute_path(path):
    return os.path.abspath(os.getcwd()) + "/" + path
