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
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

game = Game()

clients = {}      # socket -> player_id
buffers = {}      # socket -> buffer
next_pid = 1      # unique player id

print("Server running on", HOST, PORT)

while True:
    rlist, _, _ = select.select(
        [server] + list(clients.keys()),
        [],
        [],
        0.05
    )

    for sock in rlist:

        # ---------- NEW CONNECTION ----------
        if sock is server:
            conn, addr = server.accept()
            conn.setblocking(False)

            pid = str(next_pid)
            next_pid += 1

            clients[conn] = pid
            buffers[conn] = ""

            game.add_player(pid)

            # 🔑 (optional but recommended)
            send(conn, {"type": "init", "id": pid})

            print(f"Player {pid} joined from {addr}")

        # ---------- EXISTING CLIENT ----------
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
                        game.move_player(
                            clients[sock],
                            cmd["dx"],
                            cmd["dy"]
                        )

            except:
                pid = clients[sock]
                print(f"Player {pid} disconnected")

                game.remove_player(pid)
                del clients[sock]
                del buffers[sock]
                sock.close()

    # ---------- BROADCAST STATE ----------
    state = {
        "type": "state",
        **game.state_dict()
    }

    for c in list(clients.keys()):
        try:
            send(c, state)
        except:
            pass
