import socket
import select
import json
import time

HOST = "127.0.0.1"
PORT = 5555
FPS = 30

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

print(f"Server running on {HOST} {PORT}")

clients = {}      # sock -> player_id
players = {}      # player_id -> data
next_player_id = 1

def send(sock, data):
    try:
        sock.sendall((json.dumps(data) + "\n").encode())
    except:
        pass

def broadcast(data):
    for sock in list(clients.keys()):
        send(sock, data)

clock = time.time()

while True:
    readable, _, _ = select.select([server] + list(clients.keys()), [], [], 0)

    for sock in readable:
        # ---- NEW CONNECTION ----
        if sock is server:
            client, addr = server.accept()
            client.setblocking(False)

            pid = str(next_player_id)
            next_player_id += 1

            clients[client] = pid
            players[pid] = {
                "x": 100 + int(pid) * 60,
                "y": 200,
                "state": "normal"
            }

            print(f"Player {pid} joined from {addr}")

            send(client, {
                "type": "init",
                "id": pid
            })

        # ---- CLIENT MESSAGE ----
        else:
            try:
                data = sock.recv(4096).decode()
                if not data:
                    raise ConnectionResetError

                for line in data.split("\n"):
                    if not line.strip():
                        continue

                    msg = json.loads(line)
                    pid = clients[sock]

                    if msg["type"] == "move":
                        players[pid]["x"] += msg["dx"] * 5
                        players[pid]["y"] += msg["dy"] * 5

            except:
                pid = clients[sock]
                print(f"Player {pid} disconnected")

                del clients[sock]
                del players[pid]
                sock.close()

    # ---- BROADCAST GAME STATE ----
    if time.time() - clock > 1 / FPS:
        clock = time.time()

        broadcast({
            "type": "state",
            "game_state": "playing",
            "players": players
        })
