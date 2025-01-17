import math
import random
from ponglogic.utils import Utils

class Ball:
    FAST_VELOCITY = 15
    NORMAL_VELOCITY = 10
    SLOW_VELOCITY = 8

    BIG_RADIUS = 20
    NORMAL_RADIUS = 10
    SMALL_RADIUS = 5

    def __init__(self):
        self.radius = self.NORMAL_RADIUS
        self.x = 500
        self.y = 300
        self.angle = 0
        self.velocity = self.NORMAL_VELOCITY
        self.direction = {
            "facing_up": False,
            "facing_down": False,
            "facing_right": False,
            "facing_left": False,
        }
        self.bound_angle = {
            "left_top": math.pi * 7 / 4,
            "left_bottom": math.pi / 4,
            "right_top": math.pi * 5 / 4,
            "right_bottom": math.pi * 3 / 4,
        }

    def reset_position(self):
        self.x = 500
        self.y = 300

    def reset_angle(self):
        self.angle = random.uniform(
            self.bound_angle["right_bottom"], self.bound_angle["right_top"]
        )

    def set_direction(self):
        if math.pi <= self.angle and self.angle <= math.pi * 2:
            self.direction["facing_up"] = True
            self.direction["facing_down"] = False
        else:
            self.direction["facing_up"] = False
            self.direction["facing_down"] = True
        if (math.pi / 2) <= self.angle and self.angle <= (math.pi * 3 / 2):
            self.direction["facing_left"] = True
            self.direction["facing_right"] = False
        else:
            self.direction["facing_left"] = False
            self.direction["facing_right"] = True

    def reset(self, turn_count=0):
        self.reset_position()
        self.reset_angle()
        if turn_count % 2 == 0:
            self.angle += math.pi
        self.angle = Utils.normalize_angle(self.angle)
        self.set_direction()