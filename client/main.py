import pygame
import json
from network import connect
from render import draw_player

HOST, PORT = "127.0.0.1", 5555
pygame.init()

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Tag Game")
font = pygame.font.SysFont(None, 22)
clock = pygame.time.Clock()

sock = connect(HOST, PORT)
buffer = ""

players = {}
game_state = "lobby"

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    dx = dy = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_s]: dy += 1
    if keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_d]: dx += 1

    if dx or dy:
        sock.sendall((json.dumps({"type":"move","dx":dx,"dy":dy})+"\n").encode())

    try:
        data = sock.recv(4096).decode()
        buffer += data
        while "\n" in buffer:
            msg, buffer = buffer.split("\n",1)
            state = json.loads(msg)
            game_state = state["game_state"]
            players = state["players"]
    except:
        pass

    screen.fill((25,25,35))
    for pid,p in players.items():
        draw_player(screen,p,pid,font)

    ui = font.render(f"State: {game_state}", True,(255,255,255))
    screen.blit(ui,(20,20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
