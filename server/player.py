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

    def update(self, dt):
        """Update player state - required for game loop"""
        pass

    def is_frozen(self):
        """Check if player is currently frozen"""
        return time.time() < self.freeze_until

    def in_cooldown(self):
        """Check if player is in cooldown period"""
        return time.time() < self.cooldown_until

    def make_it(self, freeze_time=3, cooldown_time=2):
        """Make this player IT"""
        self.is_it = True
        self.speed = self.it_speed
        self.size = self.it_size
        self.freeze_until = time.time() + freeze_time
        self.cooldown_until = time.time() + cooldown_time

    def clear_it(self):
        """Remove IT status from this player"""
        self.is_it = False
        self.speed = self.base_speed
        self.size = self.base_size
        self.freeze_until = 0.0
        self.cooldown_until = 0.0

    def move(self, dx, dy, map_width=1200, map_height=800):
        """Move player by delta x and y"""
        if self.is_frozen():
            return

        # Apply movement with speed
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep player inside map bounds
        self.x = max(self.size, min(map_width - self.size, self.x))
        self.y = max(self.size, min(map_height - self.size, self.y))

    def can_tag(self):
        """Check if player can tag others"""
        return self.is_it and not self.is_frozen() and not self.in_cooldown()

    def collides_with(self, other_player):
        """Check collision with another player"""
        dist = math.hypot(self.x - other_player.x, self.y - other_player.y)
        return dist < (self.size + other_player.size)

    def to_dict(self):
        """Convert player to dictionary for network transmission"""
        return {
            "x": self.x,
            "y": self.y,
            "is_it": self.is_it,
            "freeze": max(0, self.freeze_until - time.time()),
            "cooldown": max(0, self.cooldown_until - time.time()),
            "size": self.size,
            "speed": self.speed
        }