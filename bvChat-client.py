from socket import *
from sys import argv as a
import threading

if len(a) < 3:
    exit('Not enough arguments\nUsage: python3 bvChat-client.py <serverIP> <serverPort>')
elif len(a) > 3:
    exit('Too many arguments\nUsage: python3 bvChat-client.py <serverIP> <serverPort>')

commands = ['/who', '/exit', '/tell <username> <text>', '/motd', '/me', '/help']


def getLine(conn):
    msg = b''
    while True:
        ch = conn.recv(1)
        msg += ch
        if ch == b'\n' or len(ch) == 0:
            break
    return msg.decode()

serverIP = a[1]
serverPort = int(a[2])
clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect( (serverIP, serverPort) )

userName = input('Username: ')
clientSock.send((userName + '\n').encode())

confirm = clientSock.recv(1).decode()

def messageRecvr():
    global connected
    while connected:
        message = getLine(clientSock).rstrip()
        if message != '':
            print(message)

if confirm == '1':
   #password
   clientSock.send( (input('Password: ') + '\n').encode())
   passCheck = clientSock.recv(1).decode()
   if passCheck == '0':
       exit('Wrong password, try again')
elif confirm == '0':
    #new password
    clientSock.send((input('New Password: ') + '\n').encode())
elif confirm == '2':
    exit(f'{userName} already connected')
else:
    #bad
    print('bad')

try:
    connected = True
    threading.Thread(target=messageRecvr, daemon=True).start()
    motd = clientSock.recv(1024).decode()
    print("Message of the day:\n"+motd)
    while connected:
        message = input('> ')
        clientSock.send( (message + '\n').encode() )
        if message == '/exit':
            clientSock.close()
            connected = False
        if message == '/help':
            print("Valid commands: ")
            print(commands)
        if message == '/who':
            msg = clientSock.recv(1024).decode()
            print(msg)
        if message == '/motd':
            msg = clientSock.recv(1024).decode()
            print(msg)
        #if '/me' in message:
            
        #if '/tell' in message:

except Exception:
    print('Exception happened, closing connection')
    clientSock.close()