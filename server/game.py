#Control game states (freeze → playing)
#Randomly select the “It” player
#Handle tag detection (distance check)
#3-second freeze after tagging
#Cooldown to prevent instant re-tagging
#Update player speed and size states
#Synchronize all player states

import random
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

        for p in self.players.values():
            p.clear_it()

        it_player = random.choice(list(self.players.values()))
        it_player.make_it(FREEZE_TIME, COOLDOWN_TIME)

    def update(self, dt):
        if self.state == "freeze":
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.state = "playing"

        for p in self.players.values():
            p.update(dt)

        self.handle_tags()

    def handle_tags(self):
        it_players = [p for p in self.players.values() if p.is_it and not p.is_frozen()]

        for it in it_players:
            for target in self.players.values():
                if it.id == target.id:
                    continue
                if target.is_it:
                    continue
                if target.is_frozen():
                    continue
                if it.in_cooldown():
                    continue

                dist = math.hypot(it.x - target.x, it.y - target.y)
                if dist < TAG_RADIUS:
                    it.clear_it()
                    target.make_it(FREEZE_TIME, COOLDOWN_TIME)
                    return
