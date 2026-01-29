import time

class Player:
    def __init__(self, pid):
        self.id = pid
        self.x = 200
        self.y = 200

        # movement
        self.base_speed = 3
        self.it_speed = 5
        self.speed = self.base_speed

        # CAT SIZE (head radius)
        self.base_size = 20
        self.it_size = 12 
        self.size = self.base_size

        self.is_it = False
        self.freeze_until = 0
        self.cooldown_until = 0

        # shape is fixed (UI already assumes cat)
        self.shape = "cat"

    def frozen(self):
        return time.time() < self.freeze_until

    def cooldown(self):
        return time.time() < self.cooldown_until

    def make_it(self):
        self.is_it = True
        self.speed = self.it_speed
        self.size = self.it_size
        self.freeze_until = time.time() + 3
        self.cooldown_until = time.time() + 2


    def clear_it(self):
        self.is_it = False
        self.speed = self.base_speed
        self.size = self.base_size


    def to_dict(self):
        return {
            "x": int(self.x),
            "y": int(self.y),

            "is_it": self.is_it,
            "freeze": max(0, self.freeze_until - time.time()),
            "cooldown": max(0, self.cooldown_until - time.time()),

            # UI depends on this
            "size": int(self.size)
        }

