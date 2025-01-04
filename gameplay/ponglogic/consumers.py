import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
# import random
import math
from .utils import Utils
from .objects.pong_info import PongInfo

class PongLogic(AsyncWebsocketConsumer):
    pong_info_map = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # PongLogic
    async def game_loop(self):
        try:
            from gamesetting.models import GameSetting
            game_setting = await sync_to_async(GameSetting.objects.get)(id=self.pong_info.setting_id)
            Utils.set_game_setting(self.pong_info, game_setting)
        except Exception as e:
            print(f"Error retrieving for GameSetting: {e}")
        await self.send_pong_data(True)
        turn_count = 0
        while self.pong_info.score.left < 15 and self.pong_info.score.right < 15:
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
            # 上下の壁衝突判定
            if (
                Utils.has_collided_with_wall(self.pong_info.ball, self.pong_info.game_window)
                == True
            ):
                ball_velocity["y"] *= -1
                self.pong_info.ball.angle = 2 * math.pi - self.pong_info.ball.angle
                self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
                self.pong_info.ball.set_direction()

            # 左パドル衝突判定
            if (
                Utils.has_collided_with_paddle_left(
                    self.pong_info.ball, self.pong_info.paddle
                )
                == True
            ):
                is_left = True
                # 左パドル上部の衝突判定
                if (
                    Utils.has_collided_with_paddle_top(
                        self.pong_info.ball, self.pong_info.paddle, is_left
                    )
                    == True
                ):
                    is_top = True
                else:
                    is_top = False
                Utils.update_ball_angle(
                    self.pong_info.ball, self.pong_info.paddle, is_left, is_top
                )
                ball_velocity["x"], ball_velocity["y"] = Utils.update_ball_velocity(
                    is_top, ball_velocity
                )
            # 右パドル衝突判定
            elif (
                Utils.has_collided_with_paddle_right(
                    self.pong_info.ball, self.pong_info.paddle, self.pong_info.game_window
                )
                == True
            ):
                is_left = False
                # 右パドル上部衝突判定
                if (
                    Utils.has_collided_with_paddle_top(
                        self.pong_info.ball, self.pong_info.paddle, is_left
                    )
                    == True
                ):
                    is_top = True
                else:
                    is_top = False
                Utils.update_ball_angle(
                    self.pong_info.ball, self.pong_info.paddle, is_left, is_top
                )
                ball_velocity["x"], ball_velocity["y"] = Utils.update_ball_velocity(
                    is_top, ball_velocity
                )

            # 障害物衝突判定
            if (self.pong_info.is_obstacle_exist == True):
                if (
                    Utils.has_collided_with_obstacles_top_or_bottom(self.pong_info.ball, self.pong_info.obstacle1)
                    == True
                    or
                    Utils.has_collided_with_obstacles_top_or_bottom(self.pong_info.ball, self.pong_info.obstacle2)
                    == True
                ):
                    ball_velocity["y"] *= -1
                    self.pong_info.ball.angle = 2 * math.pi - self.pong_info.ball.angle
                    self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
                    self.pong_info.ball.set_direction()
                if (
                    Utils.has_collided_with_obstacles_left_or_right(self.pong_info.ball, self.pong_info.obstacle1)
                    == True
                    or
                    Utils.has_collided_with_obstacles_left_or_right(self.pong_info.ball, self.pong_info.obstacle2)
                    == True
                ):
                    ball_velocity["x"] *= -1
                    self.pong_info.ball.angle = math.pi - self.pong_info.ball.angle
                    self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
                    self.pong_info.ball.set_direction()

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
            elif self.pong_info.ball.x + self.pong_info.ball.radius < 0:
                self.pong_info.score.right += 1
                self.pong_info.state = "stop"

    async def connect(self):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        print(f"setting_id: {setting_id}")
        group_name = f"game_{setting_id}"
        await self.accept()
        await self.channel_layer.group_add(group_name, self.channel_name)
        if setting_id not in self.pong_info_map:
            self.pong_info_map[setting_id] = self.pong_info = PongInfo(setting_id, group_name)
            try:
                self.pong_info.task["game_loop"] = asyncio.create_task(self.game_loop())
            except Exception as e:
                print(f"Error creating game_loop task: {e}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.pong_info.group_name, self.channel_name)
        self.pong_info.task["game_loop"].cancel()
        del self.pong_info_map[self.pong_info.setting_id]

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        key = data.get("key")
        action = data.get("action")
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        pong_info = self.pong_info_map[setting_id]

        if key == "D" and action == "pressed":
            if (
                pong_info.paddle.left_y + 3
                <= pong_info.game_window.height - pong_info.paddle.height
            ):
                pong_info.paddle.left_y += 3
        elif key == "E" and action == "pressed":
            if pong_info.paddle.left_y - 3 >= 0:
                pong_info.paddle.left_y -= 3
        elif key == "K" and action == "pressed":
            if (
                pong_info.paddle.right_y + 3
                <= pong_info.game_window.height - pong_info.paddle.height
            ):
                pong_info.paddle.right_y += 3
        elif key == "I" and action == "pressed":
            if pong_info.paddle.right_y - 3 >= 0:
                pong_info.paddle.right_y -= 3

        if pong_info.state == "stop":
            await self.send_pong_data()

    async def handle_other_message(self, message):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        pong_info = self.pong_info_map[setting_id]
        # その他のメッセージに対応する処理
        print(f"Other message received: {message}")
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

    async def send_message(self, event):
        pong_data = event["content"]
        await self.send(text_data=json.dumps(pong_data))
