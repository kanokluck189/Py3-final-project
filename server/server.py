import socket
import select
import json
from game import Game
from protocol import send

HOST = "127.0.0.1"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

game = Game()
clients = {}
buffers = {}

print("Server running...")

while True:
    rlist, _, _ = select.select([server] + list(clients.keys()), [], [], 0.05)

    for sock in rlist:
        if sock is server:
            conn, _ = server.accept()
            conn.setblocking(False)
            pid = str(len(clients) + 1)
            clients[conn] = pid
            buffers[conn] = ""
            game.add_player(pid)
            print("Player joined:", pid)
        else:
            try:
                data = sock.recv(1024).decode()
                if not data:
                    raise ConnectionError
                buffers[sock] += data

                while "\n" in buffers[sock]:
                    msg, buffers[sock] = buffers[sock].split("\n", 1)
                    cmd = json.loads(msg)

                    if cmd["type"] == "move":
                        game.move_player(clients[sock], cmd["dx"], cmd["dy"])
            except:
                pid = clients[sock]
                del clients[sock]
                del buffers[sock]
                del game.players[pid]
                sock.close()

    state = {"type": "state", **game.state_dict()}
    for c in clients:
        send(c, state)
