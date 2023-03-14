from socket import *
from sys import argv as a

if len(a) < 3:
    exit('Not enough arguments\nUsage: python3 bvChat-client.py <serverIP> <serverPort>')
elif len(a) > 3:
    exit('Too many arguments\nUsage: python3 bvChat-client.py <serverIP> <serverPort>')

serverIP = a[1]
serverPort = a[2]
clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect( (serverIP, serverPort) )

userName = input('Username: ')
clientSock.send((userName + '\n').encode())

confirm = clientSock.recv(1)
if confirm == '1':
    #password
elif confirm == '0':
    #new password
else:
    #bad

commands = ['/who', '/exit', '/tell <username> <text>', '/motd', '/me', '/help']


