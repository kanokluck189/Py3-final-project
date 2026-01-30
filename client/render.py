import pygame

# -----------------------------
# Color presets
# -----------------------------
COLOR_NORMAL = (180, 180, 220)   # blue-ish
COLOR_IT = (255, 120, 120)       # red
COLOR_FROZEN = (130, 130, 130)   # gray
COLOR_TEXT = (255, 255, 255)

DEFAULT_SIZE = 18


def draw_player(screen, player, pid, font):
    """
    Draw a single player on screen

    player dict example:
    {
        "x": 200,
        "y": 150,
        "is_it": False,
        "freeze": 0,
        "size": 18
    }
    """

    # ---- Safe read (防 crash) ----
    x = int(player.get("x", 0))
    y = int(player.get("y", 0))
    size = int(player.get("size", DEFAULT_SIZE))

    is_it = player.get("is_it", False)
    freeze = player.get("freeze", 0)

    # ---- Color logic ----
    color = COLOR_NORMAL

    if is_it:
        color = COLOR_IT
    elif freeze > 0:
        color = COLOR_FROZEN

    # ---- Draw body ----
    pygame.draw.circle(screen, color, (x, y), size)

    # ---- Draw player id ----
    name_surface = font.render(str(pid), True, COLOR_TEXT)
    name_rect = name_surface.get_rect(
        center=(x, y - size - 12)
    )
    screen.blit(name_surface, name_rect)


def draw_all_players(screen, players, font):
    """
    Draw all players from players dict

    players example:
    {
        "1": {...},
        "2": {...}
    }
    """
    for pid, player in players.items():
        draw_player(screen, player, pid, font)
