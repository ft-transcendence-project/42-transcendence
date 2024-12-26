import math
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class GameWindow:
    def __init__(self):
        self.width = 1000
        self.height = 600

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

class Paddle:
    def __init__(self):
        self.width = 15
        self.height = 120
        self.left_y = 240
        self.right_y = 240

class Obstacle:
    def __init__(self, id):
        self.x = 250
        if id == 1:
            self.y = 135
        elif id == 2:
            self.y = 435
        self.width = 0
        self.height = 0
        self.velocity = 2

class Blind:
    def __init__(self):
        self.x = 350
        self.y = 0
        self.width = 0
        self.height = 0

class Score:
    def __init__(self):
        self.left = 0
        self.right = 0


class PongInfo:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.state = "stop"
        self.task = {}
        self.setting_id = None
        self.group_name = None
        self.game_window = GameWindow()
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = Score()
        self.obstacle1 = Obstacle(1)
        self.obstacle2 = Obstacle(2)
        self.blind = Blind()

    def reset_ball_position(self):
        self.ball.x = 500
        self.ball.y = 300

    def reset_ball_angle(self):
        self.ball.angle = random.uniform(
            self.ball.bound_angle["right_bottom"], self.ball.bound_angle["right_top"]
        )
