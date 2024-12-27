import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
# import random
import math
from .utils import Utils
from .pong_info import PongInfo

# from channels.db import database_sync_to_async
# from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
# from websocket.serializers import GameStateSerializer

class PongLogic(AsyncWebsocketConsumer):
    pong_info_map = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # PongLogic
    async def game_loop(self):
        turn_count = 0
        try:
            from gameplay.models import GameSetting
            setting = await sync_to_async(GameSetting.objects.get)(id=self.pong_info.setting_id)
            ball_size_choise = setting.ball_size
            ball_v_choise = setting.ball_velocity
            map_choise = setting.map
            print(f"map: {map_choise}, ball_size: {ball_size_choise}, ball_v: {ball_v_choise}")
            if ball_size_choise == "big":
                self.pong_info.ball.radius = 20
            elif ball_size_choise == "normal":
                self.pong_info.ball.radius = 10
            elif ball_size_choise == "small":
                self.pong_info.ball.radius = 5
            if ball_v_choise == "fast":
                self.pong_info.ball.velocity = 7
            elif ball_v_choise == "normal":
                self.pong_info.ball.velocity = 5
            elif ball_v_choise == "slow":
                self.pong_info.ball.velocity = 3
            if map_choise == "b":
                self.pong_info.obstacle_exist = True
                self.pong_info.obstacle1.width = 500
                self.pong_info.obstacle1.height = 30
                self.pong_info.obstacle2.width = 500
                self.pong_info.obstacle2.height = 30
            elif map_choise == "c":
                self.pong_info.blind.width = 300
                self.pong_info.blind.height = 600
            print(f"map: {map_choise}, ball_size: {self.pong_info.ball.radius}, ball_v: {self.pong_info.ball.velocity}")
        except Exception as e:
            print(f"Error retrieving for GameSetting: {e}")
        await self.send_pos(True)
        while self.pong_info.score.left < 15 and self.pong_info.score.right < 15:
            async with self.pong_info.lock:
                if self.pong_info.state == "stop":
                    self.pong_info.reset_ball_position()
                    self.pong_info.reset_ball_angle()
                    if turn_count % 2 == 0:
                        self.pong_info.ball.angle += math.pi
                    self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
                    turn_count += 1
                    Utils.set_direction(self.pong_info.ball)
                # print("angle: ", self.ball.angle)
                # print("direction: ", self.ball.direction["facing_up"], self.ball.direction["facing_down"], self.ball.direction["facing_right"], self.ball.direction["facing_left"])
            await self.rendering()
            await self.update_pos()
            await self.check_game_state()
        await self.send_pos()

    async def rendering(self):
        await self.send_pos()
        await asyncio.sleep(0.005)
        if self.pong_info.state == "stop":
            await asyncio.sleep(2)
            self.pong_info.state = "running"

    async def update_pos(self):
        async with self.pong_info.lock:
            # self.ball.angle = math.pi / 3 #test用
            velocity = {
                "x": self.pong_info.ball.velocity * math.cos(self.pong_info.ball.angle),
                "y": self.pong_info.ball.velocity * math.sin(self.pong_info.ball.angle),
            }
            # 上下の壁衝突判定
            if (
                Utils.has_collided_with_wall(self.pong_info.ball, self.pong_info.game_window)
                == True
            ):
                velocity["y"] *= -1
                self.pong_info.ball.angle = 2 * math.pi - self.pong_info.ball.angle
                self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
                Utils.set_direction(self.pong_info.ball)

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
                velocity["x"], velocity["y"] = Utils.update_ball_velocity(
                    is_top, velocity
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
                velocity["x"], velocity["y"] = Utils.update_ball_velocity(
                    is_top, velocity
                )

            # 障害物衝突判定
            if (self.pong_info.obstacle_exist == True):
                if (
                    Utils.has_collided_with_obstacles_top_or_bottom(self.pong_info.ball, self.pong_info.obstacle1)
                    == True
                    or
                    Utils.has_collided_with_obstacles_top_or_bottom(self.pong_info.ball, self.pong_info.obstacle2)
                    == True
                ):
                    velocity["y"] *= -1
                    self.pong_info.ball.angle = 2 * math.pi - self.pong_info.ball.angle
                    self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
                    Utils.set_direction(self.pong_info.ball)
                if (
                    Utils.has_collided_with_obstacles_left_or_right(self.pong_info.ball, self.pong_info.obstacle1)
                    == True
                    or
                    Utils.has_collided_with_obstacles_left_or_right(self.pong_info.ball, self.pong_info.obstacle2)
                    == True
                ):
                    velocity["x"] *= -1
                    self.pong_info.ball.angle = math.pi - self.pong_info.ball.angle
                    self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
                    Utils.set_direction(self.pong_info.ball)
            
            self.pong_info.ball.angle = Utils.normalize_angle(self.pong_info.ball.angle)
            Utils.set_direction(self.pong_info.ball)
            Utils.adjust_ball_position(
                self.pong_info.ball, self.pong_info.paddle, velocity, self.pong_info.game_window, self.pong_info.obstacle_exist, self.pong_info.obstacle1, self.pong_info.obstacle2
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
        # # channel_layerの全属性を取得
        # attributes = dir(self.channel_layer)
        # print("Channel Layer Attributes:")
        # for attr in attributes:
        #     try:
        #         value = getattr(self.channel_layer, attr)
        #         print(f"{attr}: {value}")
        #     except:
        #         print(f"{attr}: <unable to get value>")

        if setting_id not in self.pong_info_map:
            self.pong_info = PongInfo()
            self.pong_info.setting_id = setting_id
            self.pong_info.group_name = group_name
            self.pong_info_map[setting_id] = self.pong_info
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
            await self.send_pos()

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

    async def send_pos(self, first=False):
        setting_id = self.scope["url_route"]["kwargs"]["settingid"]
        pong_info = self.pong_info_map[setting_id]
        if (first):
            response_message = {
                "id": pong_info.setting_id,
                "left_paddle_y": pong_info.paddle.left_y,
                "right_paddle_y": pong_info.paddle.right_y,
                "ball_x": pong_info.ball.x,
                "ball_y": pong_info.ball.y,
                "ball_radius": pong_info.ball.radius,
                "obstacle1_x": pong_info.obstacle1.x,
                "obstacle1_y": pong_info.obstacle1.y,
                "obstacle1_width": pong_info.obstacle1.width,
                "obstacle1_height": pong_info.obstacle1.height,
                "obstacle2_x": pong_info.obstacle2.x,
                "obstacle2_y": pong_info.obstacle2.y,
                "obstacle2_width": pong_info.obstacle2.width,
                "obstacle2_height": pong_info.obstacle2.height,
                "blind_x": pong_info.blind.x,
                "blind_y": pong_info.blind.y,
                "blind_width": pong_info.blind.width,
                "blind_height": pong_info.blind.height,
                "left_score": pong_info.score.left,
                "right_score": pong_info.score.right,
            }
        else:
            response_message = {
                "id": pong_info.setting_id,
                "left_paddle_y": pong_info.paddle.left_y,
                "right_paddle_y": pong_info.paddle.right_y,
                "ball_x": pong_info.ball.x,
                "ball_y": pong_info.ball.y,
                "left_score": pong_info.score.left,
                "right_score": pong_info.score.right,
            }
        await self.channel_layer.group_send(
            pong_info.group_name,
            {
                "type": "send_message",
                "content": response_message,
            },
        )

    async def send_message(self, event):
        # print("sened_message")
        # contentの中にある辞書を取り出し
        message = event["content"]
        # 辞書をjson型にする
        await self.send(text_data=json.dumps(message))
