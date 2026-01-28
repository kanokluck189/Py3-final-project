import json

def send(sock, data):
    sock.sendall((json.dumps(data) + "\n").encode())
