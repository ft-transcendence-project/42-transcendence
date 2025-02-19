import asyncio

from .components import Ball, Blind, GameWindow, Obstacle, Paddle, Score


class PongInfo:
    def __init__(self, setting_id, group_name, channel_name):
        self.lock = asyncio.Lock()
        self.state = "stop"
        self.task = {}
        self.setting_id = setting_id
        self.group_name = group_name
        self.is_game_started = False
        self.game_window = GameWindow()
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = Score()
        self.is_obstacle_exist = False
        self.obstacle1 = Obstacle(1)
        self.obstacle2 = Obstacle(2)
        self.blind = Blind()
        self.player_cnt = 0
        self.is_remote = False
        self.remote_right = {"status": False, "channel_name": None}
        self.remote_left = {"status": False, "channel_name": None}
        self.is_end = False
