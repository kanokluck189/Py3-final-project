#Handle socket connections (many players)
#Receive movement input from clients
#Run the main server loop
#Broadcast updated game state to all clients

import socket
import time
import threading
import random
from player import Player
from game import Game
from protocol import encode, decode

HOST = "0.0.0.0"
PORT = 5555

# Global game state
game = Game()
clients = {}
player_id_counter = 0
clients_lock = threading.Lock()


def client_thread(conn, pid):
    """Handle individual client connection"""
    global game
    
    print(f"[Thread] Player {pid} handler started")
    
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            
            if not data:
                print(f"[Thread] Player {pid} disconnected (no data)")
                break

            # Process each message
            messages = data.strip().split('\n')
            for msg_str in messages:
                if not msg_str:
                    continue
                
                try:
                    msg = decode(msg_str)
                    
                    with clients_lock:
                        if pid not in game.players:
                            break
                        
                        player = game.players[pid]
                        
                        # Handle movement
                        if msg["type"] == "move":
                            # Only allow movement if game is playing and not frozen
                            if game.state == "playing" and not player.is_frozen():
                                dx = msg.get("dx", 0)
                                dy = msg.get("dy", 0)
                                
                                # Use the player's move method
                                player.move(dx, dy, 1200, 800)
                                
                                # Debug print
                                # print(f"[Move] Player {pid} moved to ({player.x:.1f}, {player.y:.1f})")
                        
                except Exception as e:
                    print(f"[Error] Processing message from player {pid}: {e}")
                    
    except Exception as e:
        print(f"[Error] Client thread for player {pid}: {e}")
    
    finally:
        # Clean up on disconnect
        with clients_lock:
            if pid in clients:
                del clients[pid]
            if pid in game.players:
                del game.players[pid]
                print(f"[Cleanup] Player {pid} removed from game")
        
        try:
            conn.close()
        except:
            pass


def broadcast_state():
    """Send current game state to all connected clients"""
    with clients_lock:
        if not clients:
            return
        
        # Build state message
        state = {
            "type": "state",
            "game_state": game.state,
            "players": {}
        }
        
        # Add all player data
        for pid, player in game.players.items():
            state["players"][str(pid)] = player.to_dict()
        
        # Encode once
        encoded_state = encode(state)
        
        # Send to all clients
        for pid, conn in list(clients.items()):
            try:
                conn.sendall(encoded_state)
            except Exception as e:
                print(f"[Error] Sending to player {pid}: {e}")


def check_tags():
    """Check for tag collisions between IT player and others"""
    with clients_lock:
        if game.state != "playing":
            return
        
        # Find IT players who can tag
        for it_player in game.players.values():
            if not it_player.can_tag():
                continue
            
            # Check collision with other players
            for target in game.players.values():
                if target.id == it_player.id:
                    continue
                if target.is_it:
                    continue
                if target.is_frozen():
                    continue
                
                # Check collision
                if it_player.collides_with(target):
                    print(f"[Tag] Player {it_player.id} tagged Player {target.id}!")
                    
                    # Transfer IT status
                    it_player.clear_it()
                    target.make_it(freeze_time=3, cooldown_time=2)
                    
                    return  # Only one tag per update


def main():
    """Main server loop"""
    global player_id_counter
    
    # Create server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    server.setblocking(False)
    
    print("=" * 60)
    print("PEEPAT SERVER")
    print("=" * 60)
    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for players to connect...\n")
    
    last_time = time.time()
    last_broadcast = time.time()
    
    while True:
        # Accept new connections
        try:
            conn, addr = server.accept()
            conn.setblocking(True)
            
            with clients_lock:
                pid = player_id_counter
                player_id_counter += 1
                
                # Create player at random position
                x = random.randint(100, 1100)
                y = random.randint(100, 700)
                
                player = Player(pid, x, y)
                game.add_player(player)
                clients[pid] = conn
                
                print(f"✓ Player {pid} connected from {addr}")
                print(f"  Position: ({x}, {y})")
                print(f"  Total players: {len(game.players)}\n")
                
                # Start handler thread
                threading.Thread(target=client_thread, args=(conn, pid), daemon=True).start()
                
                # Start round if we have at least 2 players
                if len(game.players) >= 2 and game.state == "freeze":
                    if not any(p.is_it for p in game.players.values()):
                        game.start_round()
                        print("🎮 Game started! Random player is IT\n")
                
        except BlockingIOError:
            pass
        except Exception as e:
            print(f"[Error] Accepting connection: {e}")
        
        # Update game state
        now = time.time()
        dt = now - last_time
        last_time = now
        
        game.update(dt)
        
        # Check for tags
        check_tags()
        
        # Broadcast state (30 times per second)
        if now - last_broadcast >= 0.033:
            broadcast_state()
            last_broadcast = now
        
        # Small sleep to prevent CPU spinning
        time.sleep(0.01)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer shutting down...")