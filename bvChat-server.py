from socket import *
import os.path
import threading
#random is used to choose motd
import random

def getLine(conn):
    msg = b''
    while True:
        ch = conn.recv(1)
        msg += ch
        if ch == b'\n' or len(ch) == 0:
            break
    return msg.decode()

userFile = 'users.txt'

port = 42424
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSock.bind( ('',port) )
serverSock.listen(15) # Maximum of 15 chatters at once

print(f'Running on {port}')


if not os.path.isfile(userFile):
    open(userFile, 'w').write('')    

users = open(userFile, 'r').read().split('\n')
users = users[:len(users)-1]
userDict = {}
connectedUsers = []

#moved to be visible by handleClient function
commands = ['/who', '/exit', '/tell <username> <text>', '/motd', '/me', '/help']

#only want to get it once per "day" (session)
motd = random.choice(open("motd.txt").read().splitlines())

if users != '':
    for user in users:
        userLi = user.split(':')
        uName = userLi[0]
        uPass = userLi[1]
        userDict.update( { uName : uPass } )

def handleClient(connInfo):
    global userDict, connectedUsers
    clientConn, clientAddr = connInfo 
    clientUN = getLine(clientConn).rstrip()
    print(clientAddr)

    if clientUN in str(connectedUsers):
        # user already connected
        clientConn.send('2'.encode())
    elif clientUN in str(users):
        # user exists
        clientConn.send('1'.encode())
        uPassword = getLine(clientConn).rstrip()
        print(uPassword)
        if uPassword != userDict[clientUN]:
            # wrong password
            clientConn.send('0'.encode())
        else:
            clientConn.send('1'.encode())
            connectedUsers.append( clientUN )
    else:
        clientConn.send('0'.encode())
        uPassword = getLine(clientConn).rstrip()
        connectedUsers.append(clientUN)
        users.append(clientUN)
        userDict.update( {clientUN : uPassword} )
        with open(userFile, 'a') as f:
            f.write(clientUN + ':' + uPassword + '\n')
    

    try:
        clientConnected = True
        clientConn.send(motd.encode())
        while clientConnected:
            message = getLine(clientConn).rstrip()
            if message != '':
                print(message)
                if message in str(commands):
                    if message == '/exit':
                        clientConnected = False
                    if message == '/who':
                        clientConn.send(str(connectedUsers).encode())
                    if message == '/motd':
                        clientConn.send(motd.encode())
                else:
                    if '/tell' in message:
                        msgs = message.split()
                        tousr = msgs[1]
                        msg = " ".join(msgs[2:])
                        print(clientUN + "whispers: " +msg)
                    #if '/me' in message:



    except Exception:
        print('Exception occurred, closing connection')

    clientConn.close()
    print(connectedUsers)
    connectedUsers.remove(clientUN)
    print(connectedUsers)


running = True
while running:
    try:
        threading.Thread(target=handleClient, args=(serverSock.accept(),), daemon=True).start()
    except KeyboardInterrupt:
        print('\n[Shutting down]')
        running = False

serverSock.close()
