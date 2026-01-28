import pygame

def draw_player(screen, p, pid, font):
    x, y = int(p["x"]), int(p["y"])
    size = p["size"]

    color = (180,180,220)
    if p["is_it"]:
        color = (255,120,120)
    if p["freeze"] > 0:
        color = (130,130,130)

    pygame.draw.circle(screen, color, (x,y), size)
    txt = font.render(pid, True, (255,255,255))
    screen.blit(txt, (x-6, y-size-20))
