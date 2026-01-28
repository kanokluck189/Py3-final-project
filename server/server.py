#Handle socket connections (many players)
#Receive movement input from clients
#Run the main server loop
#Broadcast updated game state to all clients

import socket
import time
import threading
from player import Player
from game import Game
from protocol import encode, decode

HOST = "0.0.0.0"
PORT = 5555

game = Game()
clients = {}
player_id_counter = 0

def client_thread(conn, pid):
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            msg = decode(data)
            player = game.players[pid]

            if msg["type"] == "move" and game.state == "playing":
                dx = msg["dx"]
                dy = msg["dy"]

                if not player.is_frozen():
                    player.x += dx * player.speed
                    player.y += dy * player.speed

        except:
            break

    conn.close()
    print(f"Player {pid} disconnected")

def broadcast_state():
    state = {
        "type": "state",
        "game_state": game.state,
        "players": {
            pid: p.to_dict() for pid, p in game.players.items()
        }
    }

    for conn in clients.values():
        try:
            conn.sendall(encode(state))
        except:
            pass

def main():
    global player_id_counter

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    server.setblocking(False)

    print("Server running...")

    last_time = time.time()

    while True:
        try:
            conn, addr = server.accept()
            conn.setblocking(True)

            pid = player_id_counter
            player_id_counter += 1

            player = Player(pid)
            game.add_player(player)
            clients[pid] = conn

            threading.Thread(target=client_thread, args=(conn, pid), daemon=True).start()
            print(f"Player {pid} connected")

            if len(game.players) >= 2:
                game.start_round()

        except BlockingIOError:
            pass

        now = time.time()
        dt = now - last_time
        last_time = now

        game.update(dt)
        broadcast_state()

        time.sleep(0.03)

if __name__ == "__main__":
    main()
