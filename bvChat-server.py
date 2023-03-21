from socket import *
import os.path
import threading

def getLine(conn):
    msg = b''
    while True:
        ch = conn.recv(1)
        msg += ch
        if ch == b'\n' or len(ch) == 0:
            break
    return msg.decode()

userFile = 'users.txt'

port = 55553
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

commands = ['/who', '/exit', '/tell <username> <text>', '/motd', '/me', '/help']

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
            connectedUsers.append( (clientUN, connInfo) )
    else:
        clientConn.send('0'.encode())
        uPassword = getLine(clientConn).rstrip()
        connectedUsers.append( (clientUN, connInfo) )
        users.append(clientUN)
        userDict.update( {clientUN : uPassword} )
        with open(userFile, 'a') as f:
            f.write(clientUN + ':' + uPassword + '\n')
    

    try:
        clientConnected = True
        while clientConnected:
            message = getLine(clientConn).rstrip()
            if message != '':
                if message in str(commands):
                    if message == '/exit':
                        clientConnected = False
                        message = f'{clientUN} has left the chat'
                        print('A USER DISSCONNECTED!')
                        for i in range(0, len(connectedUsers)):
                            conn = connectedUsers[i][1][0]
                            conn.send(message.encode())
                else:
                    message = clientUN + ': ' + message + '\n'
                    print(message)
                    for i in range(0, len(connectedUsers)):
                        conn = connectedUsers[i][1][0]
                        conn.send(message.encode())


    except Exception:
        print('Exception occurred, closing connection')

    clientConn.close()
    connectedUsers.remove( (clientUN, connInfo) )


running = True
while running:
    try:
        threading.Thread(target=handleClient, args=(serverSock.accept(),), daemon=True).start()
    except KeyboardInterrupt:
        print('\n[Shutting down]')
        running = False

serverSock.close()
