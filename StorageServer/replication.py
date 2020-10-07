from threading import Thread
import socket
import sys
import os

CHUNKSIZE = 1_000_000

def replicate(connection, address):
    replicate_path_size = int.from_bytes(connection.recv(1), 'big') #receive replicate path size
    replicate_path = (connection.recv(replicate_path_size)).decode() #receive replicate path
    print("Recieved path:", replicate_path)
    number_of_ips_size = int.from_bytes(connection.recv(1), 'big') #receive number size
    number_of_ips = int((connection.recv(number_of_ips_size)).decode()) #receive number
    print("Recieved number of ips:", number_of_ips)

    ips = list()
    for i in range(number_of_ips):
        ip_size= int.from_bytes(connection.recv(1), 'big') #receive filename size
        ip = (connection.recv(ip_size)).decode() #receive filename
        ips.append(ip)
    for ip in ips:
        send_replica(ip, replicate_path)
    return

def send_replica(receiver_ip, rep_path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((receiver_ip, 10002))
    print(rep_path)
    for path,dirs,files in os.walk(rep_path):
        print(path, dirs, files)
        for file in files:
            filename = os.path.join(path,file)
            relpath = os.path.relpath(filename,'server')
            filesize = os.path.getsize(filename)

            print(f'Sending {relpath}')

            with open(filename,'rb') as f:
                sock.sendall(relpath.encode() + b'\n')
                sock.sendall(str(filesize).encode() + b'\n')

                # Send the file in chunks so large files can be handled.
                while True:
                    data = f.read(CHUNKSIZE)
                    if not data: break
                    sock.sendall(data)
    print('Done.')

def receive_replica(connection, address):
    with connection,connection.makefile('rb') as clientfile:
        while True:
            raw = clientfile.readline()
            if not raw: break # no more files, server closed connection.

            filename = raw.strip().decode()
            length = int(clientfile.readline())
            print(f'Downloading {filename}...\n  Expecting {length:,} bytes...',end='',flush=True)

            path = os.path.join('client',filename)
            os.makedirs(os.path.dirname(path),exist_ok=True)

            # Read the data in chunks so it can handle large files.
            with open(path,'wb') as f:
                while length:
                    chunk = min(length,CHUNKSIZE)
                    data = clientfile.read(chunk)
                    if not data: break
                    f.write(data)
                    length -= len(data)
                else: # only runs if while doesn't break and length==0
                    print('Complete')
                    continue

            # socket was closed early.
            print('Incomplete')
            break
