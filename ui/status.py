import pygame
import sys
import math
import random

pygame.init()

# ---------------- WINDOW ----------------
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tag Game – Proper Maze")

clock = pygame.time.Clock()

# ---------------- FONTS ----------------
font = pygame.font.SysFont("consolas", 18)

# ---------------- COLORS ----------------
BG = (16, 18, 26)
MAP_BG = (235, 238, 242)
WALL = (55, 65, 105)
PLAYER = (140, 170, 255)
TEXT = (220, 220, 220)
TP_COLOR = (120, 180, 255)

# ---------------- PLAYER ----------------
player = {
    "x": 120,
    "y": 120,
    "r": 14,
    "speed": 4,
    "last_tp": 0
}

TP_COOLDOWN_MS = 2000
TP_RADIUS = 18

# ---------------- MAZE (CONNECTED + WIDE) ----------------
WALLS = [
    # Outer border
    pygame.Rect(30, 30, 840, 20),
    pygame.Rect(30, 550, 840, 20),
    pygame.Rect(30, 30, 20, 540),
    pygame.Rect(850, 30, 20, 540),

    # Vertical walls (short, with BIG gaps)
    pygame.Rect(200, 30, 20, 160),
    pygame.Rect(200, 260, 20, 160),

    pygame.Rect(380, 100, 20, 160),
    pygame.Rect(380, 330, 20, 160),

    pygame.Rect(560, 30, 20, 160),
    pygame.Rect(560, 260, 20, 160),

    pygame.Rect(740, 100, 20, 160),
    pygame.Rect(740, 330, 20, 160),

    # Horizontal connectors (wide lanes)
    pygame.Rect(200, 190, 200, 20),
    pygame.Rect(380, 260, 200, 20),
    pygame.Rect(560, 190, 200, 20),

    pygame.Rect(100, 430, 300, 20),
    pygame.Rect(500, 430, 300, 20),
]

# ---------------- TELEPORTS ----------------
TELEPORTS = [
    pygame.Vector2(70, 70),
    pygame.Vector2(830, 70),
    pygame.Vector2(70, 530),
    pygame.Vector2(830, 530),
]

# ---------------- HELPERS ----------------
def draw_text(text, x, y):
    screen.blit(font.render(text, True, TEXT), (x, y))

def draw_teleport(pos, t):
    for i in range(4):
        r = TP_RADIUS + i * 4 + int(3 * math.sin(t / 250 + i))
        pygame.draw.circle(screen, TP_COLOR, pos, r, 2)

def draw_cat(x, y):
    pygame.draw.circle(screen, PLAYER, (x, y), 14)

    pygame.draw.polygon(screen, PLAYER, [
        (x - 10, y - 8),
        (x - 4, y - 20),
        (x - 2, y - 8)
    ])
    pygame.draw.polygon(screen, PLAYER, [
        (x + 10, y - 8),
        (x + 4, y - 20),
        (x + 2, y - 8)
    ])

    pygame.draw.circle(screen, (20, 20, 20), (x - 4, y - 2), 2)
    pygame.draw.circle(screen, (20, 20, 20), (x + 4, y - 2), 2)

def collides(x, y):
    rect = pygame.Rect(x - 12, y - 12, 24, 24)
    return any(rect.colliderect(w) for w in WALLS)

def check_teleport():
    now = pygame.time.get_ticks()
    if now - player["last_tp"] < TP_COOLDOWN_MS:
        return

    pos = pygame.Vector2(player["x"], player["y"])
    for tp in TELEPORTS:
        if pos.distance_to(tp) < TP_RADIUS:
            dest = random.choice([t for t in TELEPORTS if t != tp])
            player["x"], player["y"] = int(dest.x), int(dest.y)
            player["last_tp"] = now
            break

# ---------------- MAIN LOOP ----------------
running = True
while running:
    clock.tick(60)
    t = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------- MOVEMENT --------
    keys = pygame.key.get_pressed()
    dx = dy = 0

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy -= player["speed"]
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy += player["speed"]
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx -= player["speed"]
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx += player["speed"]

    if not collides(player["x"] + dx, player["y"]):
        player["x"] += dx
    if not collides(player["x"], player["y"] + dy):
        player["y"] += dy

    check_teleport()

    # -------- DRAW --------
    screen.fill(BG)
    pygame.draw.rect(screen, MAP_BG, (30, 30, 840, 540), border_radius=12)

    for wall in WALLS:
        pygame.draw.rect(screen, WALL, wall, border_radius=6)

    for tp in TELEPORTS:
        draw_teleport(tp, t)

    draw_cat(player["x"], player["y"])

    draw_text("WASD / Arrows to move", 20, 10)
    draw_text("Teleport cooldown: 2 seconds", 20, 30)

    pygame.display.flip()

pygame.quit()
sys.exit()
