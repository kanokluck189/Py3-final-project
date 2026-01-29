import socket
import select
import json
from game import Game
from protocol import send

# ------------ CONFIG ------------
HOST = "127.0.0.1"
PORT = 5555
# --------------------------------

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

game = Game()
clients = {}     # socket -> player_id
buffers = {}     # socket -> incoming buffer

print("Server running...")

while True:
    # listen to server socket + all client sockets
    rlist, _, _ = select.select(
        [server] + list(clients.keys()),
        [],
        [],
        0.05
    )

    for sock in rlist:
        # ---- New connection ----
        if sock is server:
            conn, _ = server.accept()
            conn.setblocking(False)

            pid = str(len(clients) + 1)
            clients[conn] = pid
            buffers[conn] = ""

            game.add_player(pid)
            print("Player joined:", pid)

        # ---- Existing client ----
        else:
            try:
                data = sock.recv(1024).decode()
                if not data:
                    raise ConnectionError

                buffers[sock] += data

                while "\n" in buffers[sock]:
                    msg, buffers[sock] = buffers[sock].split("\n", 1)
                    cmd = json.loads(msg)

                    # ---- MOVEMENT ----
                    if cmd["type"] == "move":
                        game.move_player(
                            clients[sock],
                            cmd["dx"],
                            cmd["dy"]
                        )

            except:
                # ---- Disconnect ----
                pid = clients[sock]
                print("Player left:", pid)

                del clients[sock]
                del buffers[sock]
                del game.players[pid]
                sock.close()

    # ---- Broadcast game state ----
    state = {
        "type": "state",
        **game.state_dict()
    }

    for c in clients:
        send(c, state)
