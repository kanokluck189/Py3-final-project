#Handle socket connections (many players)
#Receive movement input from clients
#Run the main server loop
#Broadcast updated game state to all clients
#captain

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
player_id = 0

def client_thread(conn, pid):
    global game
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            msg = decode(data)
            player = game.players[pid]

            if msg["type"] == "move":
                if game.state == "playing" and player.freeze_timer <= 0:
                    player.x += msg["dx"] * player.speed
                    player.y += msg["dy"] * player.speed

        except:
            break

    conn.close()

def broadcast_state():
    state = {
        "type": "state",
        "game_state": game.state,
        "players": {
            pid: {
                "x": p.x,
                "y": p.y,
                "is_it": p.is_it,
                "freeze": p.freeze_timer,
                "cooldown": p.cooldown,
                "size": p.size
            } for pid, p in game.players.items()
        }
    }

    for p in game.players.values():
        try:
            p.conn.sendall(encode(state))
        except:
            pass

def main():
    global player_id

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

            pid = player_id
            player_id += 1

            player = Player(pid, conn)
            game.add_player(player)

            threading.Thread(target=client_thread, args=(conn, pid)).start()
            print(f"Player {pid} connected")

            if len(game.players) >= 2:
                game.start_round()

        except:
            pass

        now = time.time()
        dt = now - last_time
        last_time = now

        game.update(dt)
        broadcast_state()

        time.sleep(0.03)

if __name__ == "__main__":
    main()
