import socket
import select
import json

HOST = "127.0.0.1"
PORT = 5555

print("RUNNING SERVER FILE:", __file__)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

clients = {}   # socket -> player_id
positions = {} # player_id -> {x,y}
buffers = {}
next_pid = 1

print("Server running on", HOST, PORT)

while True:
    rlist, _, _ = select.select(
        [server] + list(clients.keys()),
        [],
        [],
        0.05
    )

    for sock in rlist:

        # ---- NEW CONNECTION ----
        if sock is server:
            print("SERVER: incoming connection...")
            conn, addr = server.accept()
            conn.setblocking(False)

            pid = str(next_pid)
            next_pid += 1

            clients[conn] = pid
            buffers[conn] = ""
            positions[pid] = {"x": 400, "y": 300}

            print(f"Player {pid} joined from {addr}")

            # send init
            conn.sendall(
                (json.dumps({
                    "type": "init",
                    "id": pid
                }) + "\n").encode()
            )

        # ---- EXISTING CLIENT ----
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
                        pid = clients[sock]
                        positions[pid]["x"] += cmd["dx"] * 5
                        positions[pid]["y"] += cmd["dy"] * 5

            except:
                pid = clients[sock]
                print(f"Player {pid} disconnected")

                del positions[pid]
                del buffers[sock]
                del clients[sock]
                sock.close()

    # ---- BROADCAST STATE ----
    state = {
        "type": "state",
        "players": positions
    }

    for c in list(clients.keys()):
        try:
            c.sendall((json.dumps(state) + "\n").encode())
        except:
            pass
