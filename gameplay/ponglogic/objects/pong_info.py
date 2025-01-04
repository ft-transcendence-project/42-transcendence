import random
import asyncio
from .components import Ball, Paddle, Score, Obstacle, Blind, GameWindow

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
        self.is_obstacle_exist = False
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
