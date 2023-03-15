from socket import *
from sys import argv as a

if len(a) < 3:
    exit('Not enough arguments\nUsage: python3 bvChat-client.py <serverIP> <serverPort>')
elif len(a) > 3:
    exit('Too many arguments\nUsage: python3 bvChat-client.py <serverIP> <serverPort>')

serverIP = a[1]
serverPort = int(a[2])
clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect( (serverIP, serverPort) )

userName = input('Username: ')
clientSock.send((userName + '\n').encode())

confirm = clientSock.recv(1).decode()
if confirm == '1':
   #password
   clientSock.send( (input('Password: ') + '\n').encode())
   passCheck = clientSock.recv(1).decode()
   if passCheck == '0':
       exit('Wrong password, try again')
elif confirm == '0':
    #new password
    clientSock.send((input('New Password: ') + '\n').encode())
elif confirm == '3':
    exit(f'{userName} already connected')
else:
    #bad
    print('bad')

commands = ['/who', '/exit', '/tell <username> <text>', '/motd', '/me', '/help']

clientSock.close()
