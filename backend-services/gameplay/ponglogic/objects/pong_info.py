import asyncio

from .components import Ball, Blind, GameWindow, Obstacle, Paddle, Score


class PongInfo:
    def __init__(self, setting_id, group_name, channel_name):
        self.lock = asyncio.Lock()
        self.state = "stop"
        self.task = {}
        self.setting_id = setting_id
        self.group_name = group_name
        self.channel_name = channel_name
        self.is_game_started = False
        self.game_window = GameWindow()
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = Score()
        self.is_obstacle_exist = False
        self.obstacle1 = Obstacle(1)
        self.obstacle2 = Obstacle(2)
        self.blind = Blind()
        self.channel_cnt = 0
        self.remote_right = False
        self.remote_left = False
