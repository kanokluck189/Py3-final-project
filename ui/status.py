# Display:
# Freeze countdown (3 seconds)
# Player state (It / frozen / cooldown)
# Show basic instructions

import socket
import pygame
import json

# ---------------- CONFIG ----------------
HOST = "127.0.0.1"
PORT = 5555
WIDTH, HEIGHT = 800, 600
FPS = 60
# ----------------------------------------

# ---- Connect to server ----
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.setblocking(False)

# ---- Helper: send JSON command ----
def send_cmd(cmd):
    try:
        sock.sendall((json.dumps(cmd) + "\n").encode())
    except:
        pass

# ---- Pygame setup ----
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tag Game - Digital Cat UI")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)

players = {}
game_state = "freeze"
my_id = "0"
buffer = ""

# ---- Cat drawing function (UI ONLY) ----
def draw_cat(screen, x, y, size, color, frozen=False):
    pygame.draw.circle(screen, color, (x, y), size)

    ear_offset = size
    ear_height = size

    left_ear = [
        (x - ear_offset, y - size // 2),
        (x - size // 2, y - ear_height),
        (x - size // 6, y - size // 2),
    ]

    right_ear = [
        (x + size // 6, y - size // 2),
        (x + size // 2, y - ear_height),
        (x + ear_offset, y - size // 2),
    ]

    pygame.draw.polygon(screen, color, left_ear)
    pygame.draw.polygon(screen, color, right_ear)

    eye_y = y - size // 6
    eye_x_offset = size // 3
    eye_radius = max(2, size // 6)

    eye_color = (80, 80, 80) if frozen else (0, 0, 0)
    pygame.draw.circle(screen, eye_color, (x - eye_x_offset, eye_y), eye_radius)
    pygame.draw.circle(screen, eye_color, (x + eye_x_offset, eye_y), eye_radius)

    nose_y = y + size // 6
    pygame.draw.circle(screen, (255, 150, 150), (x, nose_y), eye_radius // 2)

# ---- Main loop ----
running = True
while running:
    # -------- Events --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------- Movement input --------
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    speed = 4

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy = -speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy = speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx = -speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx = speed

    if dx != 0 or dy != 0:
        send_cmd({
            "type": "move",
            "dx": dx,
            "dy": dy
        })

    # -------- Network receive --------
    try:
        data = sock.recv(4096).decode()
        buffer += data

        while "\n" in buffer:
            msg, buffer = buffer.split("\n", 1)
            state = json.loads(msg)

            if state["type"] == "state":
                game_state = state["game_state"]
                players = state["players"]

    except BlockingIOError:
        pass

    # -------- Draw --------
    screen.fill((25, 25, 35))

    for pid, p in players.items():
        x = int(p["x"])
        y = int(p["y"])
        size = int(p["size"])

        color = (180, 180, 220)
        if p["is_it"]:
            color = (255, 120, 120)
        if p["freeze"] > 0:
            color = (130, 130, 130)

        draw_cat(screen, x, y, size, color, frozen=p["freeze"] > 0)

        id_text = font.render(pid, True, (220, 220, 220))
        screen.blit(id_text, (x - 6, y - size - 22))

    # ---- UI text ----
    state_text = font.render(f"State: {game_state}", True, (220, 220, 220))
    screen.blit(state_text, (20, 20))

    if my_id in players and players[my_id]["is_it"]:
        it_text = font.render("YOU ARE IT", True, (255, 100, 100))
        screen.blit(it_text, (20, 45))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

sock.close() 
