import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
# import random
import logging
import math
from .utils import Utils
from .objects.pong_info import PongInfo

logger = logging.getLogger('ponglogic')

# from channels.db import database_sync_to_async
# from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
# from websocket.serializers import GameStateSerializer

SCORE_TO_WIN = 15

class PongLogic(AsyncWebsocketConsumer):
    pong_info_map = {}

    def __init__(self, *args, **kwargs):
        self.group_name = None
        super().__init__(*args, **kwargs)

    # PongLogic
    async def game_loop(self):
        try:
            from gamesetting.models import GameSetting
            game_setting = await sync_to_async(GameSetting.objects.get)(id=self.pong_info.setting_id)
            Utils.set_game_setting(self.pong_info, game_setting)
        except Exception as e:
            logger.error(f"Error retrieving for GameSetting: {e}")
        await self.send_pong_data(True)
        turn_count = 0
        while self.pong_info.score.left < SCORE_TO_WIN and self.pong_info.score.right < SCORE_TO_WIN:
            async with self.pong_info.lock:
                if self.pong_info.state == "stop":
                    self.pong_info.ball.reset(turn_count)
                    turn_count += 1
            await self.rendering()
            await self.update_pos()
            await self.check_game_state()
        await self.send_pong_data()

    async def rendering(self):
        await self.send_pong_data()
        await asyncio.sleep(0.005)
        if self.pong_info.state == "stop":
            await asyncio.sleep(2)
            self.pong_info.state = "running"

    async def update_pos(self):
        async with self.pong_info.lock:
            ball_velocity = {
                "x": self.pong_info.ball.velocity * math.cos(self.pong_info.ball.angle),
                "y": self.pong_info.ball.velocity * math.sin(self.pong_info.ball.angle),
            }

            Utils.walls_collision(ball_velocity, self.pong_info)
            Utils.paddles_collision(ball_velocity, self.pong_info)
            Utils.obstacles_collision(ball_velocity, self.pong_info)
            self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
            self.pong_info.ball.set_direction()
            Utils.adjust_ball_position(
                self.pong_info.ball, self.pong_info.paddle, ball_velocity, self.pong_info.game_window, self.pong_info.is_obstacle_exist, self.pong_info.obstacle1, self.pong_info.obstacle2
            )

    async def check_game_state(self):
        async with self.pong_info.lock:
            if (
                self.pong_info.ball.x - self.pong_info.ball.radius
                > self.pong_info.game_window.width
            ):
                self.pong_info.score.left += 1
                self.pong_info.state = "stop"
                if self.pong_info.score.left >= SCORE_TO_WIN:
                    await self.send_game_over_message("left")
            elif self.pong_info.ball.x + self.pong_info.ball.radius < 0:
                self.pong_info.score.right += 1
                self.pong_info.state = "stop"
                if self.pong_info.score.right >= SCORE_TO_WIN:
                    await self.send_game_over_message("right")

    async def connect(self):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        logger.info(f"setting_id: {setting_id}")
        group_name = f"game_{setting_id}"
        self.group_name = group_name
        await self.accept()
        await self.channel_layer.group_add(group_name, self.channel_name)
        if setting_id not in self.pong_info_map:
            self.pong_info_map[setting_id] = self.pong_info = PongInfo(setting_id, group_name, self.channel_name)
            try:
                self.pong_info.task["game_loop"] = asyncio.create_task(self.game_loop())
            except Exception as e:
                logger.error(f"Error creating game_loop task: {e}")

    async def disconnect(self, close_code):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if setting_id in self.pong_info_map:
            if self.pong_info_map[setting_id].channel_name == self.channel_name:
                self.pong_info.task["game_loop"].cancel()
                del self.pong_info_map[self.pong_info.setting_id]

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        user_input = Utils.extract_to_dict(data)
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        pong_info = self.pong_info_map[setting_id]

        Utils.apply_user_input_to_paddle(user_input, pong_info)
        if pong_info.state == "stop":
            await self.send_pong_data()

    async def handle_other_message(self, message):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        pong_info = self.pong_info_map[setting_id]
        logger.info(f"Other message received: {message}")
        # その他のメッセージに対応する処理
        response_message = {"message": f"Received: {message}"}
        await self.channel_layer.group_send(
            pong_info.group_name,
            {
                "type": "send_message",
                "content": response_message,
            },
        )

    async def send_pong_data(self, first=False):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        pong_info = self.pong_info_map[setting_id]
        await self.channel_layer.group_send(
            pong_info.group_name,
            {
                "type": "send_message",
                "content": Utils.generate_pong_data(pong_info, first),
            },
        )

    async def send_game_over_message(self, winner):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        pong_info = self.pong_info_map[setting_id]
        await self.channel_layer.group_send(
            pong_info.group_name,
            {
                "type": "send_message",
                "content": Utils.generate_game_over_message(pong_info, winner),
            },
        )

    async def send_message(self, event):
        pong_data = event["content"]
        await self.send(text_data=json.dumps(pong_data))
