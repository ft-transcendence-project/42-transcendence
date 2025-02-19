import asyncio
import json
import logging
import math
from datetime import datetime

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .objects.pong_info import PongInfo
from .utils import Utils

from django.core.cache import cache
from channels.layers import get_channel_layer
from channels.exceptions import ChannelFull

logger = logging.getLogger("ponglogic")

SCORE_TO_WIN = 15
RESET_DURATION = 2
UPDATE_RATE_HZ = 60


class PongLogic(AsyncWebsocketConsumer):
    # インスタンス間で共有(クラス変数)
    pong_info_map = {}

    def __init__(self, *args, **kwargs):
        self.group_name = None
        super().__init__(*args, **kwargs)

    async def game_loop(self):
        try:
            from gamesetting.models import GameSetting

            game_setting = await sync_to_async(GameSetting.objects.get)(
                id=self.pong_info.setting_id
            )
            Utils.set_game_setting(self.pong_info, game_setting)
        except Exception as e:
            logger.error(f"Error retrieving for GameSetting: {e}")
        await self.send_pong_data(True)
        while self.pong_info.is_game_started == False:
            await asyncio.sleep(1 / UPDATE_RATE_HZ)
        turn_count = 0
        while (self.pong_info.is_end == False and self.pong_info.score.left < SCORE_TO_WIN and self.pong_info.score.right < SCORE_TO_WIN):
            async with self.pong_info.lock:
                if self.pong_info.state == "stop":
                    self.pong_info.ball.reset(turn_count)
                    turn_count += 1
            await self.rendering()
            await self.update_pos()
            await self.check_game_state()
        await self.send_pong_data()

    async def rendering(self):
        async with self.pong_info.lock:
            if self.pong_info.is_end == True:
                return
        await self.send_pong_data()
        await asyncio.sleep(1 / UPDATE_RATE_HZ)
        start_time = datetime.now()
        if self.pong_info.state == "stop":
            while (datetime.now() - start_time).total_seconds() < RESET_DURATION:
                self.pong_info.paddle.update_position(self.pong_info.game_window)
                await self.send_pong_data()
                await asyncio.sleep(1 / UPDATE_RATE_HZ)
            self.pong_info.state = "running"

    async def update_pos(self):
        async with self.pong_info.lock:
            self.pong_info.paddle.update_position(self.pong_info.game_window)
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
                self.pong_info.ball,
                self.pong_info.paddle,
                ball_velocity,
                self.pong_info.game_window,
                self.pong_info.is_obstacle_exist,
                self.pong_info.obstacle1,
                self.pong_info.obstacle2,
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
                    self.pong_info.is_end = True
                    await self.send_game_over_message("left")
            elif self.pong_info.ball.x + self.pong_info.ball.radius < 0:
                self.pong_info.score.right += 1
                self.pong_info.state = "stop"
                if self.pong_info.score.right >= SCORE_TO_WIN:
                    self.pong_info.is_end = True
                    await self.send_game_over_message("right")

    async def connect(self):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        logger.info(f"setting_id: {setting_id}")
        print("user: ",self.scope["user"])
        group_name = f"game_{setting_id}"
        self.group_name = group_name
        await self.accept()
        print("accept")
        await self.channel_layer.group_add(group_name, self.channel_name)
        if setting_id in self.pong_info_map:
            self.pong_info = self.pong_info_map[setting_id]
            async with self.pong_info.lock:
                if self.pong_info.is_remote == True and self.pong_info.is_end == True:
                    await self.channel_layer.send(self.channel_name, {
                        "type": "send_message",
                        "content": {
                        "type": "reload",
                        },
                    })
                    if self.pong_info != None:
                        del self.pong_info_map[self.pong_info.setting_id] 
                    return
            await self.send_pong_data(True)
        if setting_id not in self.pong_info_map:
            self.pong_info_map[setting_id] = self.pong_info = PongInfo(
                setting_id, group_name, self.channel_name
            )
            try:
                self.pong_info.task["game_loop"] = asyncio.create_task(self.game_loop())
            except Exception as e:
                logger.error(f"Error creating game_loop task: {e}")
        self.pong_info.player_cnt += 1
        print(f"{self.pong_info.setting_id} -> connect player_cnt: {self.pong_info.player_cnt}")
        if self.pong_info.player_cnt > 2:
            await self.send_channel_message("full")

    async def disconnect(self, close_code):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        async with self.pong_info.lock:
            logger.info(f"setting_id: {setting_id}")
            if self.pong_info.player_cnt > 0:
                self.pong_info.player_cnt -= 1
                print(f"{setting_id} -> disconnect player_cnt: {self.pong_info.player_cnt}")
            if self.pong_info.is_remote == False and self.pong_info.player_cnt == 0:
                self.pong_info.task["game_loop"].cancel()
                del self.pong_info_map[self.pong_info.setting_id]
                return
            if self.pong_info.player_cnt == 0 and self.pong_info.setting_id in self.pong_info_map:
                del self.pong_info_map[self.pong_info.setting_id]
                return
            if self.pong_info.is_remote == True and self.pong_info.is_game_started == False:
                self.pong_info.is_end = True
                if self.channel_name == self.pong_info.remote_left["channel_name"]:
                    self.pong_info.remote_left = False
                    await self.send_channel_message(self.pong_info.remote_right["channel_name"], {
                        "type":"interrupted before start" })
                else:
                    self.pong_info.remote_right = False
                    await self.send_channel_message(self.pong_info.remote_left["channel_name"], {
                        "type":"interrupted before start" }) 
                return
            if self.pong_info.is_remote == True and self.pong_info.is_end == False:
                self.pong_info.is_end = True
                await self.send_group_message("interrupted")

    async def receive(self, text_data=None):
        pong_data = json.loads(text_data)
        async with self.pong_info.lock:
            if pong_data.get("game_signal", None) == "start":
                self.pong_info.is_game_started = True
                await self.send_group_message("start_OK")
            elif pong_data.get("type", None) == "remote_ON":
                await self.set_remote_mode(pong_data)
            elif pong_data.get("type", None) == "remote_OFF":
                if pong_data.get("remote_player_pos",None) == "right":
                    self.pong_info.remote_right = False
                else:
                    self.pong_info.remote_left = False
            elif pong_data.get("type", None) == "received interrupted":
                await self.handle_unexpected_disconnection(pong_data)
            elif pong_data.get("type", None) == "tournament":
                self.pong_info.is_tournament = True
            elif pong_data.get("type", None) == "game_over":
                self.pong_info.task["game_loop"].cancel()
            else:
                self.pong_info.paddle.set_instruction(pong_data)

    async def set_remote_mode(self,pong_data):
        if pong_data.get("remote_player_pos",None) == "right":
            self.pong_info.remote_right = {"status": True, "channel_name": self.channel_name}
            print(f"remote_right: {self.pong_info.remote_right}")
        elif pong_data.get("remote_player_pos",None) == "left":
            self.pong_info.remote_left = {"status": True, "channel_name": self.channel_name}
            print(f"remote_left: {self.pong_info.remote_left}")
        if self.pong_info.player_cnt == 2 and self.pong_info.remote_left["channel_name"] != self.pong_info.remote_right["channel_name"] and self.pong_info.remote_left["status"] == True and self.pong_info.remote_right["status"] == True:
            await self.send_channel_message(self.pong_info.remote_left["channel_name"],{
            "type": "remote_OK",
            "player": "left" })
            await self.send_channel_message(self.pong_info.remote_right["channel_name"], {
            "type": "remote_OK",
            "player": "right" })
            self.pong_info.is_remote = True

    async def handle_unexpected_disconnection(self,pong_data):
        if "game_loop" in self.pong_info.task and self.pong_info.task["game_loop"]:
            self.pong_info.task["game_loop"].cancel()
        if self.pong_info.is_game_started == False:
            await self.send_group_message("interrupted before start")
            return
        if pong_data.get("winner",None) == "right":
            winner = "right"
        elif pong_data.get("winner",None) == "left":
            winner = "left"
        await self.send_game_over_message(winner)

    async def send_group_message(self,message):
        await self.channel_layer.group_send(
            self.pong_info.group_name,
            {
                "type": "send_message",
                "content": {
                    "type": message,
                },
            },
        )

    async def send_channel_message(self,channel_name, message):
        await self.channel_layer.send(
            channel_name,
            {
                "type": "send_message",
                "content": message,
            },
        )

    async def send_pong_data(self, first=False):
        await self.channel_layer.group_send(
            self.pong_info.group_name,
            {
                "type": "send_message",
                "content": Utils.generate_pong_data(self.pong_info, first),
            },
            )

    async def send_game_over_message(self, winner):
        await self.channel_layer.group_send(
            self.pong_info.group_name,
            {
                "type": "send_message",
                "content": Utils.generate_game_over_message(self.pong_info,winner),
            },
        )

    async def send_message(self, event):
        pong_data = event["content"]
        await self.send(text_data=json.dumps(pong_data))
