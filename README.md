# [F20] Distributed Systems Project 2
Distributed file system implementation.
### Team: Sausage Party

# How to launch the system:
### Prerequisite requirements
* Ubuntu OS
* Installed Docker Compose

### Client
* Clone docker-compose file for client from GitHub repository
* run docker-compose 
```
docker-compose up
```
### Name server
* Clone docker-compose file for name server from GitHub repository
* run docker-compose 
```
docker-compose up
```
### Storage server
* Clone docker-compose file for storage from GitHub repository
* run docker-compose 
```
docker-compose up
```
# Architectural diagram
![Architecture diagram](https://i.ibb.co/m4SrnHb/123456.png)

# Description of communication protocols
### General queries:  
* ***TODO*** ```help```                                                      : get information about available commands

* ```init <username> <password>```                                : initialization of a new file system under specified username
![Init diagram](https://i.ibb.co/X4Fn456/INIT.png)
* ```login <username> <password>```                               : continue using your filesystem
![Login diagram](https://i.ibb.co/28Wnvmm/login.png)
* ***TODO*** ```exit```                                                      : finish you session

### File queries:
* ```get <path>/<filename>```                                     : download a file to a local system (reading)
![Get diagram](https://i.ibb.co/vV7Wphj/get.png)
* ```put filename <path>```                                       : put a local file to the filesystem at the specified destination
![Put diagram](https://i.ibb.co/SBMhcnP/put.png)
* ***TODO*** ??? ```touch <path>/<filename>```                               : ??? It will also support certain directory operations - listing, creation... ???
* ```rm <path>/<filename>```                                      : remove a specified file
![RM diagram](https://i.ibb.co/QHnQYp7/rm.png)
* ```cp <path from>/<filename> <path to>/<filename>```            : copy the content of the file to the different target file
![CP diagram](https://i.ibb.co/thPST39/cp.png)
* ```mv <path from>/<filename> <path to>/<filename>```            : move a file to the new destination
![MV diagram](https://i.ibb.co/VWvs88S/mv.png)

### Directory queries:
* ***TODO*** ```ls```                                                        : list contents of the current working directory
* ```mkdir <directory>```                                         : create a new directory
![MKDIR diagram](https://i.ibb.co/tKbL5QT/mkdir.png)
* ***TODO*** ```cd <destination>```                                          : change current working directory  
* ```rmd <directory>```                                           : remove a directory
![rmd diagram](https://i.ibb.co/TbKD94h/rmd.png)
