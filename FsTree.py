import random
import socket


class FsTree:
    def __init__(self, name: str):
        self.name = name
        self.path = ""
        self.address = ""
        self.replicas = []
        self.children = []
        self.syncr = False

    def set_path(self, path: str):
        self.path = path

    def set_sync(self, value: bool):
        self.syncr = value

    def add_child(self, child):
        if child not in self.children:
            child.set_path(self.path + "/" + child.name)
            child.set_replicas(random.sample(self.replicas, k=3))
            child.set_address(random.choice(child.replicas))
            self.children.append(child)
        return True

    def set_replicas(self, replicas):
        self.replicas = replicas
        for child in self.children:
            child.set_replicas(replicas)
        self.syncr = False
        return True

    def set_address(self, address: str):
        self.address = address

    def remove_child(self, child_name):
        for child in self.children:
            if child.name == child_name:
                self.children.remove(child)
                return True

    def get_child(self, path: str):
        if path == '':
            return self

        folders = path.split('/')

        for child in self.children:
            if child.name == folders[0]:
                return child.get_child('/'.join(folders[1:]))

        return False

    def list_children(self):
        response = []
        for child in self.children:
            response.append(child.name)
        return response

    def sync(self):
        port = 10000
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.address, port))

        command = "sync"

        sock.send(len(command).to_bytes(1, 'big'))
        sock.send(command.encode())

        sock.send(len(self.path).to_bytes(1, 'big'))
        sock.send(self.path.encode())

        size = len(self.replicas)
        sock.sendall(len(str(size)).to_bytes(1, 'big')) #sending size
        sock.sendall(str(size).encode())

        for replica in self.replicas:
        	if replica != self.address:
        	    sock.send(len(replica).to_bytes(1, 'big'))
        	    sock.send(replica.encode())
