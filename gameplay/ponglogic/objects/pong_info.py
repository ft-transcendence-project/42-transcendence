import asyncio
from .components import Ball, Paddle, Score, Obstacle, Blind, GameWindow

class PongInfo:
    def __init__(self, setting_id, group_name):
        self.lock = asyncio.Lock()
        self.state = "stop"
        self.task = {}
        self.setting_id = setting_id
        self.group_name = group_name
        self.game_window = GameWindow()
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = Score()
        self.is_obstacle_exist = False
        self.obstacle1 = Obstacle(1)
        self.obstacle2 = Obstacle(2)
        self.blind = Blind()
