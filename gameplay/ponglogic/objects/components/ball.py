import math
import random

class Ball:
    def __init__(self):
        self.radius = 10
        self.x = 500
        self.y = 300
        self.angle = 0
        self.velocity = 5
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