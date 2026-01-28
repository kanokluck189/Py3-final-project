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

    # Called every game tick
    def update(self, dt):
        pass  # movement handled via move()

    # State checks
    def is_frozen(self):
        """Check if player is currently frozen"""
        return time.time() < self.freeze_until

    def in_cooldown(self):
        """Check if player is in cooldown period"""
        return time.time() < self.cooldown_until

    # Role control
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

    # MOVEMENT
    def move(self, dx, dy, map_width=800, map_height=600):
        if self.is_frozen():
            return

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep inside map
        self.x = max(self.size, min(map_width - self.size, self.x))
        self.y = max(self.size, min(map_height - self.size, self.y))

    # Collision / Tagging
    def collides_with(self, other):
        dist = math.hypot(self.x - other.x, self.y - other.y)
        return dist < (self.size + other.size)

    # Network
    def to_dict(self):
        """Convert player to dictionary for network transmission"""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "is_it": self.is_it,
            "freeze": max(0, self.freeze_until - time.time()),
            "cooldown": max(0, self.cooldown_until - time.time()),
            "size": self.size
        }