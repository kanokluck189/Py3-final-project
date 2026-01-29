import pygame
import json
from network import connect
from render import draw_player
from ui.status import StatusUI

HOST, PORT = "127.0.0.1", 5555

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tag Game - Multiplayer Cats")
font = pygame.font.SysFont(None, 22)
clock = pygame.time.Clock()

# ---- UI ----
status_ui = StatusUI(font)

# ---- Network ----
sock = connect(HOST, PORT)
sock.setblocking(False)
buffer = ""

players = {}
game_state = "lobby"
my_id = None   # ได้จาก server (init)

running = True
while running:
    # -------- Events --------
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # -------- Input --------
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

    if dx or dy:
        try:
            sock.sendall(
                (json.dumps({
                    "type": "move",
                    "dx": dx,
                    "dy": dy
                }) + "\n").encode()
            )
        except:
            pass

    # -------- Network receive --------
    try:
        data = sock.recv(4096).decode()
        buffer += data

        while "\n" in buffer:
            msg, buffer = buffer.split("\n", 1)
            state = json.loads(msg)

            # 🔑 รับ id จาก server
            if state.get("type") == "init":
                my_id = state["id"]
                print("My ID:", my_id)

            # 🔄 game state
            elif state.get("type") == "state":
                game_state = state["game_state"]
                players = state["players"]

    except BlockingIOError:
        pass

    # -------- Draw --------
    screen.fill((25, 25, 35))

    for pid, p in players.items():
        draw_player(screen, p, pid, font)

    status_ui.draw(
        screen,
        game_state=game_state,
        players=players,
        my_id=my_id
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sock.close()
