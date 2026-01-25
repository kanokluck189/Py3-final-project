#Control game states (freeze → playing)
#Randomly select the “It” player
#Handle tag detection (distance check)
#3-second freeze after tagging
#Cooldown to prevent instant re-tagging
#Update player speed and size states
#Synchronize all player states
#captain

import random
import time
import math

FREEZE_TIME = 3.0
COOLDOWN_TIME = 2.0
TAG_RADIUS = 30

class Game:
    def __init__(self):
        self.players = {}
        self.state = "freeze"
        self.freeze_timer = 3.0

    def add_player(self, player):
        self.players[player.id] = player

    def start_round(self):
        self.state = "freeze"
        self.freeze_timer = 3.0

        it_player = random.choice(list(self.players.values()))
        it_player.is_it = True
        it_player.freeze_timer = FREEZE_TIME

    def update(self, dt):
        if self.state == "freeze":
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.state = "playing"

        for p in self.players.values():
            p.update(dt)

    def try_tag(self, it_player, target):
        if self.state != "playing":
            return
        if it_player.cooldown > 0:
            return

        dist = math.hypot(it_player.x - target.x, it_player.y - target.y)
        if dist < TAG_RADIUS:
            it_player.is_it = False

            target.is_it = True
            target.freeze_timer = FREEZE_TIME
            target.cooldown = COOLDOWN_TIME
            target.speed = 5
            target.size = 12
