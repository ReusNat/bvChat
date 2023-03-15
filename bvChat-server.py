from socket import *
import os.path

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
serverSock.listen()
print(f'Running on {port}')

clientConn, clientAddr = serverSock.accept()
clientUN = getLine(clientConn).rstrip()

if not os.path.isfile(userFile):
    open(userFile, 'w').write('')    

users = open(userFile, 'r').read().split('\n')
users = users[:len(users)-1]
userDict = {}
connectedUsers = []

if users != '':
    for user in users:
        userLi = user.split(':')
        uName = userLi[0]
        uPass = userLi[1]
        userDict.update( { uName : uPass } )

#print(userDict)
if clientUN in str(connectedUsers):
    clientConn.send('3'.encode())
elif clientUN in str(users):
    clientConn.send('1'.encode())
    uPassword = getLine(clientConn).rstrip()
    if uPassword != userDict[clientUN]:
        clientConn.send('0'.encode())
    else:
        connectedUsers.append(clientUN)
        clientConn.send('1'.encode())
else:
    clientConn.send('0'.encode())
    uPassword = getLine(clientConn).rstrip()
    with open(userFile, 'a') as f:
        f.write(clientUN + ':' + uPassword + '\n')


serverSock.close()
