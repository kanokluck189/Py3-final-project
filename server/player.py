# Define the Player class
# Store player properties:
# Position (x, y)
# Speed
# Size (normal / smaller)
# is_it flag
# Freeze timer
# Cooldown timer
import time
import math

class Player:
    def __init__(self, player_id, x=100, y=100):
        self.id = player_id

        # Position
        self.x = x
        self.y = y

        # Movement
        self.base_speed = 3
        self.it_speed = 5
        self.speed = self.base_speed

        # Size
        self.base_size = 20
        self.it_size = 12
        self.size = self.base_size

        # State
        self.is_it = False
        self.freeze_until = 0.0
        self.cooldown_until = 0.0

    # State checks
    def is_frozen(self):
        return time.time() < self.freeze_until

    def in_cooldown(self):
        return time.time() < self.cooldown_until

    # Role control
    def make_it(self, freeze_time=3, cooldown_time=2):
        self.is_it = True
        self.speed = self.it_speed
        self.size = self.it_size
        self.freeze_until = time.time() + freeze_time
        self.cooldown_until = time.time() + cooldown_time

    def clear_it(self):
        self.is_it = False
        self.speed = self.base_speed
        self.size = self.base_size
        self.freeze_until = 0.0
        self.cooldown_until = 0.0

    # Movement
    def move(self, dx, dy, map_width, map_height):
        if self.is_frozen():
            return

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep inside map
        self.x = max(self.size, min(map_width - self.size, self.x))
        self.y = max(self.size, min(map_height - self.size, self.y))

    # Tag detection
    def can_tag(self):
        return self.is_it and not self.is_frozen() and not self.in_cooldown()

    def collides_with(self, other_player):
        dist = math.hypot(self.x - other_player.x, self.y - other_player.y)
        return dist < (self.size + other_player.size)

    # Serialize for network
    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "is_it": self.is_it,
            "frozen": self.is_frozen()
        }
