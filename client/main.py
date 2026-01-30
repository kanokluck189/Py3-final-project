import pygame
import json
import socket
import sys
from render import draw_all_players
# DON'T initialize UI here - we'll do it later

print("RUNNING CLIENT FILE:", __file__)

# ------------ CONFIG ------------
HOST, PORT = "127.0.0.1", 5555
WIDTH, HEIGHT = 800, 600
FPS = 60
# --------------------------------

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tag Game - Multiplayer Cats")
font = pygame.font.SysFont(None, 22)
clock = pygame.time.Clock()

# ---- UI ----
# DON'T create status_ui here yet - it might need connection data
status_ui = None  # We'll create this AFTER connection is established

# ---- Network Connection ----
def connect_to_server(host, port, timeout=5):
    """Connect to server with proper error handling"""
    try:
        print(f"Attempting to connect to {host}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        print("✅ Connected successfully!")
        sock.settimeout(None)
        return sock
    except socket.timeout:
        print("❌ Connection timed out. Is the server running?")
        return None
    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure the server is running on the correct port.")
        return None
    except socket.gaierror:
        print("❌ Invalid hostname or address.")
        return None
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

# Attempt connection
sock = connect_to_server(HOST, PORT)
if sock is None:
    print("Failed to connect to server. Exiting...")
    pygame.quit()
    sys.exit(1)

# Set to non-blocking only after successful connection
sock.setblocking(False)
buffer = ""

# ---- Game State ----
players = {}
game_state = "lobby"
my_id = None
connection_established = False

print("Connected! Waiting for game data...")
running = True

while running:
    # -------- Events --------
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # -------- Input (only after connection established) --------
    if connection_established and my_id is not None:
        dx = dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # Send movement data
        if dx != 0 or dy != 0:
            try:
                move_data = json.dumps({
                    "type": "move",
                    "dx": dx,
                    "dy": dy
                }) + "\n"
                sock.sendall(move_data.encode())
            except (socket.error, BrokenPipeError) as e:
                print(f"❌ Failed to send movement data: {e}")
                running = False

    # -------- Network Receive --------
    try:
        data = sock.recv(4096).decode('utf-8')
        if not data:  # Server disconnected
            print("❌ Server disconnected")
            running = False
            continue
            
        buffer += data
        
        # Process all complete messages
        while "\n" in buffer:
            msg, buffer = buffer.split("\n", 1)
            if not msg.strip():  # Skip empty messages
                continue
                
            try:
                state = json.loads(msg)
                
                # Handle initialization
                if state.get("type") == "init":
                    my_id = state.get("id")
                    print(f"✅ Received my ID: {my_id}")
                    connection_established = True
                    
                    # NOW create the status UI after we have connection data
                    from ui.status import StatusUI
                    status_ui = StatusUI(font)
                    print("✅ Status UI initialized")
                    
                # Handle game state updates
                elif state.get("type") == "state":
                    game_state = state.get("game_state", "playing")
                    new_players = state.get("players", {})
                    
                    # Update players data safely
                    players.clear()
                    for pid, player_data in new_players.items():
                        players[pid] = {
                            "x": player_data.get("x", 0),
                            "y": player_data.get("y", 0),
                            "state": player_data.get("state", "normal")
                        }
                        
            except json.JSONDecodeError as e:
                print(f"⚠️ Invalid JSON received: {e}")
                continue
                
    except BlockingIOError:
        # No data available, continue
        pass
    except (socket.error, ConnectionResetError) as e:
        print(f"❌ Network error: {e}")
        running = False

    # -------- Draw --------
    screen.fill((25, 25, 35))
    
    # Show connection status if not established
    if not connection_established:
        text = font.render("Connecting to server...", True, (255, 255, 255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    else:
        # Draw game content
        for pid, player_data in players.items():
            draw_player(screen, player_data, pid, font)
        
        # Only draw status UI if it exists
        if status_ui is not None:
            status_ui.draw(
                screen,
                game_state=game_state,
                players=players,
                my_id=my_id
            )
        else:
            # Fallback: show basic status
            status_text = font.render(f"Game State: {game_state} | Players: {len(players)}", True, (255, 255, 255))
            screen.blit(status_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

# Cleanup
print("Closing connection...")
try:
    sock.close()
except:
    pass
pygame.quit()
sys.exit()