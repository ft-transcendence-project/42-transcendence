import math
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class SharedState:
    # lock = asyncio.Lock()
    tasks = {}

    class GameWindow:
        width = 1000
        height = 600

    class Ball:
        radius = 10
        x = 500
        y = 300
        angle = 0
        velocity = 5
        direction = {
            "facing_up": False,
            "facing_down": False,
            "facing_right": False,
            "facing_left": False,
        }
        bound_angle = {
            "left_top": math.pi * 7 / 4,
            "left_bottom": math.pi / 4,
            "right_top": math.pi * 5 / 4,
            "right_bottom": math.pi * 3 / 4,
        }

    class Paddle:
        width = 15
        height = 120
        left_y = 240
        right_y = 240

    class Obstacle:
        x = 250
        y = 100
        width = 500
        height = 30
        velocity = 2

    class blind:
        x = 350
        y = 0
        width = 300
        height = 600

    class Score:
        right = 0
        left = 0

    @classmethod
    def init(cls):
        cls.Ball.x = 500
        cls.Ball.y = 300
        cls.Ball.angle = 0
        cls.Ball.velocity = 5
        cls.Ball.direction = {
            "facing_up": False,
            "facing_down": False,
            "facing_right": False,
            "facing_left": False,
        }
        cls.Paddle.left_y = 240
        cls.Paddle.right_y = 240
        cls.Score.right = 0
        cls.Score.left = 0
        cls.Obstacle.width = 0
        cls.Obstacle.height = 0
        cls.blind.width = 0
        cls.blind.height = 0

    @classmethod
    def reset_ball_position(cls):
        cls.Ball.x = 500
        cls.Ball.y = 300

    @classmethod
    def reset_ball_angle(cls):
        cls.Ball.angle = random.uniform(
            cls.Ball.bound_angle["right_bottom"], cls.Ball.bound_angle["right_top"]
        )
