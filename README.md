# bvChat
bvChat is a chat program built in Python. The server supports 15 clients connected at any given time. Each client that logs in will have their usernames and passwords saved even if the the server goes down.
Client usernames and passwords are stored in plain text in `users.txt`.
## Server
`bvChat-server.py` can be run like a normal python program and will continue to run until a keboard interupt or an unexpected error occurs.

## Client
`bvChat-client.py` can be run with the command `python3 bvChat-client.py serverIP serverPort`. The Client will then prompt the user for a username, if the username is in the `users.txt` file then it will prompt the user for a password.
If a user puts a wrong password in three times within 30 seconds it will lock that username for 2 minutes.
