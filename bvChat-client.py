from socket import *
from sys import argv as a
import threading

# if statement to handle proper usage of the bvChat
if len(a) < 3:
    print('Not enough arguments\nUsage: python3 bvChat-client.py <serverIP>\
            <serverPort>')
    exit(1)
elif len(a) > 3:
    print('Too many arguments\nUsage: python3 bvChat-client.py <serverIP>\
            <serverPort>')
    exit(1)

commands = ['/who', '/exit', '/tell <username> <text>', '/motd', '/me', '/help']


# getLine function does exactly as it says, continue to recv bytes 
# until it gets a '\n'
def getLine(conn):
    msg = b''
    while True:
        ch = conn.recv(1)
        msg += ch
        if ch == b'\n' or len(ch) == 0:
            break
    return msg.decode()


# try/except to handle the user not passing in a valid port number
try:
    serverIP = a[1]
    serverPort = int(a[2])
except ValueError:
    print(f'{a[2]} is not an int')
    print('Usage: python3 bvChat-client.py <serverIP> <serverPort>')
    exit(1)


# try/except to make sure the server is even running
try:
    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect( (serverIP, serverPort) )
except ConnectionRefusedError:
    print(f'There is no server running on {serverIP}:{serverPort}')
    print('Try again or verify the server is running')
    exit(1)


userName = input('Username: ')
clientSock.send((userName + '\n').encode())

confirm = clientSock.recv(1).decode()

# messageRecvr handles the reciving of messages from the server
# this function is run by a thread that is opened later in the code
def messageRecvr():
    global connected
    while connected:
        message = getLine(clientSock)
        if message != '':
            print(message)


# This mess of if statements handles password validation when a client first connects
if confirm == '1':
    # Enter a password
    clientSock.send( (input('Password: ') + '\n').encode())
    passCheck = clientSock.recv(1).decode()
    if passCheck == '0':
        # Password was wrong for the supplied username
        clientSock.close()
        print('Wrong password, try again')
        exit(1)
    elif passCheck == '2':
        # You tried too many times, account is locked
        clientSock.close()
        print('Too many attempts, account locked for 2 minutes')
        exit(1)
elif confirm == '0':
    # User doesn't already exist, so make new password
    clientSock.send((input('New Password: ') + '\n').encode())
elif confirm == '2':
    # The username is already connected, can't have 2
    clientSock.close()
    print(f'{userName} already connected')
    exit(1)
elif confirm == '3':
    # Your account isn't unlocked yet from entering wrong password too many times
    clientSock.close()
    print('Nice try buddy, wait some more')
    exit(1)
else:
    # If we get this point everything has failed and I don't know what happened, so just bail
    print('bad')
    exit(1)

try:
    connected = True
    threading.Thread(target=messageRecvr, daemon=True).start()
    motd = getLine(clientSock)
    print("Message of the day:\n"+motd)
    while connected:
        message = input('> ')
        clientSock.send( (message + '\n').encode() )
        if message == '/exit':
            connected = False
            clientSock.close()
        if message == '/help':
            print("Valid commands: ")
            print(commands)

except Exception:
    print('Exception happened, closing connection')
    clientSock.close()
