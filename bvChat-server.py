from socket import *

port = 42424
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

serverSock.bind( ('',port) )
serverSock.listen()
print(f'Running on {port}')

clientConn, clientAddr = serverSock.accept()
print(clientConn.recv(1024).decode())
clientConn.send('1'.encode())


serverSock.close()
