import random
import time
from player import Player

class Game:
    def __init__(self):
        self.players = {}
        self.state = "lobby"

    def add_player(self, pid):
        self.players[pid] = Player(pid)

        if len(self.players) >= 2 and self.state == "lobby":
            self.start_game()

    def start_game(self):
        self.state = "playing"
        it_id = random.choice(list(self.players.keys()))
        self.players[it_id].make_it()

    def move_player(self, pid, dx, dy):
        p = self.players.get(pid)
        if not p or p.frozen():
            return

        p.x += dx * p.speed
        p.y += dy * p.speed

        for other in self.players.values():
            if other.id != pid and p.is_it and not p.cooldown():
                if abs(p.x - other.x) < 20 and abs(p.y - other.y) < 20:
                    p.clear_it()
                    other.make_it()

    def state_dict(self):
        return {
            "game_state": self.state,
            "players": {pid: p.to_dict() for pid, p in self.players.items()}
        }
