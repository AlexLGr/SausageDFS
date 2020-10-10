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
* ```help```                                                      : get information about available commands
* ```init <username> <password>```                                : initialization of a new file system under specified username
![Init diagram](https://i.ibb.co/X4Fn456/INIT.png)
* ```login <username> <password>```                               : continue using your filesystem
* ```exit```                                                      : finish you session

### File queries:
* ```get <path>/<filename>```                                     : download a file to a local system (reading)
* ```put filename <path>```                                       : put a local file to the filesystem at the specified destination
* ??? ```touch <path>/<filename>```                               : ??? It will also support certain directory operations - listing, creation... ???
* ```rm <path>/<filename>```                                      : remove a specified file
* ```cp <path from>/<filename> <path to>/<filename>```            : copy the content of the file to the different target file
* ```mv <path from>/<filename> <path to>/<filename>```            : move a file to the new destination

### Directory queries:
* ```ls```                                                        : list contents of the current working directory
* ```mkdir <directory>```                                         : create a new directory
* ```cd <destination>```                                          : change current working directory  
* ```rmd <directory>```                                           : remove a directory
