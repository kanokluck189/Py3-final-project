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
    # Head
    pygame.draw.circle(screen, color, (x, y), size)

    # Ears (triangles)
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

    # Eyes
    eye_y = y - size // 6
    eye_x_offset = size // 3
    eye_radius = max(2, size // 6)

    eye_color = (0, 0, 0)
    if frozen:
        eye_color = (80, 80, 80)

    pygame.draw.circle(screen, eye_color, (x - eye_x_offset, eye_y), eye_radius)
    pygame.draw.circle(screen, eye_color, (x + eye_x_offset, eye_y), eye_radius)

    # Nose
    nose_y = y + size // 6
    pygame.draw.circle(screen, (255, 150, 150), (x, nose_y), eye_radius // 2)

# ---- Main loop ----
running = True
while running:
    # -------- Events --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------- Network --------
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
    screen.fill((25, 25, 35))  # nicer background

    for pid, p in players.items():
        x = int(p["x"])
        y = int(p["y"])
        size = int(p["size"])

        # Cat colors
        color = (180, 180, 220)        # normal cat
        if p["is_it"]:
            color = (255, 120, 120)    # IT cat
        if p["freeze"] > 0:
            color = (130, 130, 130)    # frozen cat

        draw_cat(screen, x, y, size, color, frozen=p["freeze"] > 0)

        # Player ID
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

