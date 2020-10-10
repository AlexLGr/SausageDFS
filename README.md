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
"help                         : get information about available commands\n"
"init <username> <password>   : initialization of a new file system under specified username\n"
"login <username>             : continue using your filesystem\n"
"exit

```file reading, get
writing,  put 
creation, touch????
deletion, rm
copy, cp
moving mv
info queries  
It will also support certain directory operations 
listing,  ls
creation mkdir 
changing  cd
deletion rmd
