from socket import *
import os.path
import threading
from time import time
import random


# Same getLine function as in the client, just keeps recving bytes
# until it gets a '\n'
def getLine(conn):
    msg = b''
    while True:
        ch = conn.recv(1)
        msg += ch
        if ch == b'\n' or len(ch) == 0:
            break
    return msg.decode()


# Creates a server socket open on an arbitrary port
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSock.bind(('', 0))
serverSock.listen(15)  # Maximum of 15 chatters at once

print(f'Running on port: {serverSock.getsockname()[1]}')


userFile = 'users.txt'
if not os.path.isfile(userFile):
    open(userFile, 'w').write('')


# this creates all the lists an dicts that hold
# user information and connected users
users = open(userFile, 'r').read().split('\n')
users = users[:len(users)-1]
userDict = {}
connectedUsers = []
offlineMessages = {}
connAttemps = {'initUsr': [[], False]}

# List of proper commands the user can send
commands = ['/who', '/exit', '/tell <username> <text>', '/motd', '/me']

# Chooses a random line from motd.txt to send to users when they join
# there will only be one per day(session)
motd = random.choice(open("motd.txt").read().splitlines()) + '\n'

if users != '':
    for user in users:
        userLi = user.split(':')
        uName = userLi[0]
        uPass = userLi[1]
        userDict.update({uName: uPass})


# handleClient handles login of each user and the sending of messages
# funciton is called my making a thread further down the file
def handleClient(connInfo):
    global userDict, connectedUsers
    clientConnected = True
    clientConn, clientAddr = connInfo
    clientUN = getLine(clientConn).rstrip()

    # if statement to handle usernames that have attempted to login
    # and given wrong passwords
    if clientUN in connAttemps:
        if connAttemps[clientUN][1] and\
                connAttemps[clientUN][0][0] > int(time()):
            # Username is still locked
            clientConn.send('3'.encode())
            clientConnected = False
        elif connAttemps[clientUN][1] and\
                connAttemps[clientUN][0][0] < int(time()):
            # Username is no longer locked
            connAttemps[clientUN][0] = []
            connAttemps[clientUN][1] = False

    if clientConnected:
        if clientUN in str(connectedUsers):
            # User already connected
            clientConn.send('2'.encode())
        elif clientUN in str(users):
            # User exists
            clientConn.send('1'.encode())
            uPassword = getLine(clientConn).rstrip()

            if uPassword != userDict[clientUN]:
                # wrong password
                timeList = []
                if clientUN in connAttemps:
                    timeList = connAttemps[clientUN][0]
                    timeList.append(int(time()))
                else:
                    timeList = [int(time())]

                # The following if statements handle the time lock
                # on username locks
                if clientUN in connAttemps and\
                        len(connAttemps[clientUN][0]) == 3:
                    if connAttemps[clientUN][0][2] -\
                            connAttemps[clientUN][0][0] < 30:
                        # Too many attempts,
                        # so account is locked for 3 minutes
                        connAttemps[clientUN][1] = True
                        connAttemps[clientUN][0] = [int(time()) + 120]
                        clientConn.send('2'.encode())
                    else:
                        connAttemps[clientUN][0] = [int(time())]
                else:
                    connAttemps.update({clientUN: [timeList, False]})
                    clientConn.send('0'.encode())

                clientConnected = False
            else:
                clientConn.send('1'.encode())
                connectedUsers.append((clientUN, connInfo))
        else:
            # Make new user and add them to userFile
            clientConn.send('0'.encode())
            uPassword = getLine(clientConn).rstrip()
            connectedUsers.append((clientUN, connInfo))
            users.append(clientUN)
            userDict.update({clientUN: uPassword})
            with open(userFile, 'a') as f:
                f.write(clientUN + ':' + uPassword + '\n')

    try:
        if clientConnected:
            clientConn.send(motd.encode())

        if clientUN in offlineMessages and clientConnected:
            for message in offlineMessages[clientUN]:
                clientConn.send(message.encode())

        while clientConnected:
            message = getLine(clientConn).rstrip()
            if message != '':
                if message in str(commands):
                    if message == '/exit':
                        clientConnected = False
                        message = f'{clientUN} has left the chat\n'
                        print('A USER DISSCONNECTED!')
                        connectedUsers.remove((clientUN, connInfo))
                        for i in range(0, len(connectedUsers)):
                            conn = connectedUsers[i][1][0]
                            conn.send(message.encode())
                    if message == '/who':
                        for usr in connectedUsers:
                            msg = usr[0] + '\n'
                            clientConn.send(msg.encode())
                    if message == '/motd':
                        clientConn.send(motd.encode())
                else:
                    if '/tell' in message:
                        msgs = message.split()
                        del msgs[0]
                        tousr = msgs[0]
                        del msgs[0]
                        msg = " ".join(msgs)
                        msg = clientUN + " whispers: " + msg + "\n"
                        for i in range(0, len(connectedUsers)):
                            if tousr == connectedUsers[i][0]:
                                conn = connectedUsers[i][1][0]
                                conn.send(msg.encode())
                        msglist = []
                        msglist.append(msg)
                        if tousr in str(users) and\
                                tousr not in str(connectedUsers):
                            if tousr not in str(offlineMessages):
                                offlineMessages[tousr] = msglist
                            else:
                                msglist.append(offlineMessages[tousr])
                                offlineMessages[tousr] = msglist
                        print(offlineMessages)
                    elif '/me' in message:
                        msgs = message.split()
                        del msgs[0]
                        me = clientUN
                        msg = " ".join(msgs)
                        message = "* " + me + " " + msg + '\n'
                    else:
                        message = clientUN + ': ' + message + '\n'
                    print(message)
                    if "/tell" not in message:
                        for i in range(0, len(connectedUsers)):
                            conn = connectedUsers[i][1][0]
                            conn.send(message.encode())

    except KeyboardInterrupt:
        print('Exception occurred, closing connection')

    clientConn.close()


running = True
while running:
    try:
        threading.Thread(target=handleClient,
                         args=(serverSock.accept(),),
                         daemon=True).start()
    except KeyboardInterrupt:
        print('\n[Shutting down]')
        running = False

serverSock.close()
