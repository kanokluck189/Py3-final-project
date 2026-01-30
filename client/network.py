import socket

def connect(host, port):
    print("CLIENT: connecting to", host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.setblocking(False)
    print("CLIENT: connected!")
    return sock
