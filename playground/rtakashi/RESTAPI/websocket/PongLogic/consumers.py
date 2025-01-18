import asyncio
import json
import math
import random

from channels.generic.websocket import AsyncWebsocketConsumer

from .utils import Utils


class PongLogic(AsyncWebsocketConsumer):
    class game_window:
        width = 1000
        height = 600

    class ball:
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

    class paddle:
        width = 15
        height = 120
        left_y = 240
        right_y = 240

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left_score = 0
        self.right_score = 0
        self.state = "stop"
        self.turn_count = 0
        self.lock = asyncio.Lock()
        self.game_window = self.game_window()
        self.ball = self.ball()
        self.paddle = self.paddle()
        self.tasks = {}

    # PongLogic
    async def game_start(self):
        self.left_score = 0
        self.right_score = 0
        await self.game_loop()

    def get_game_state():
        from .models import GameState

        return GameState.objects.all()

    async def game_loop(self):
        while self.left_score < 15 and self.right_score < 15:
            if self.state == "stop":
                self.ball.x = self.game_window.width / 2
                self.ball.y = self.game_window.height / 2
                self.ball.angle = random.uniform(
                    self.ball.bound_angle["right_bottom"],
                    self.ball.bound_angle["right_top"],
                )
                if self.turn_count % 2 == 0:
                    self.ball.angle += math.pi
                self.ball.angle = Utils.normalize_angle(self.ball.angle)
                self.turn_count += 1
                Utils.set_direction(self.ball)
                # print("angle: ", self.ball.angle)
                # print("direction: ", self.ball.direction["facing_up"], self.ball.direction["facing_down"], self.ball.direction["facing_right"], self.ball.direction["facing_left"])
            await self.rendering()
            await self.update_pos()
            await self.check_game_state()
        await self.send_pos()

    async def rendering(self):
        await self.send_pos()
        await asyncio.sleep(0.005)
        if self.state == "stop":
            await asyncio.sleep(2)
            self.state = "running"

    async def update_pos(self):
        async with self.lock:
            # self.ball.angle = math.pi / 3 #test用
            x_velocity = self.ball.velocity * math.cos(self.ball.angle)
            y_velocity = self.ball.velocity * math.sin(self.ball.angle)

            # 上下壁との衝突
            if (
                (
                    self.ball.y + self.ball.radius >= self.game_window.height
                    and self.ball.direction["facing_down"]
                )
                or self.ball.y - self.ball.radius <= 0
                and self.ball.direction["facing_up"]
            ):
                y_velocity *= -1
                self.ball.angle = 2 * math.pi - self.ball.angle
                self.ball.angle = Utils.normalize_angle(self.ball.angle)
                Utils.set_direction(self.ball)

            # 左右パドルとの衝突
            if (
                (
                    self.ball.x - self.ball.radius == self.paddle.width
                    and self.paddle.left_y + self.paddle.height
                    >= self.ball.y - self.ball.radius
                    and self.ball.y + self.ball.radius >= self.paddle.left_y
                    and self.ball.direction["facing_left"]
                )
                or (
                    self.ball.x - self.ball.radius <= self.paddle.width
                    and self.paddle.left_y + self.paddle.height / 2 >= self.ball.y
                    and self.ball.y >= self.paddle.left_y - self.ball.radius
                    and self.ball.direction["facing_left"]
                )
                or (
                    self.ball.x - self.ball.radius <= self.paddle.width
                    and self.paddle.left_y + self.paddle.height / 2 <= self.ball.y
                    and self.ball.y
                    <= self.paddle.left_y + self.paddle.height + self.ball.radius
                    and self.ball.direction["facing_left"]
                )
            ):
                # 左パドルとの衝突
                if self.ball.y <= self.paddle.left_y + self.paddle.height / 2:
                    # パドル上部
                    collision_distance = (
                        self.paddle.left_y + self.paddle.height / 2
                    ) - self.ball.y
                    if collision_distance > self.paddle.height / 2:
                        self.ball.angle = self.ball.bound_angle.get("left_top")
                    else:
                        self.ball.angle = (
                            self.ball.bound_angle["left_top"] - 2 * math.pi
                        ) / (self.paddle.height / 2) * collision_distance + 2 * math.pi
                    x_velocity *= -1
                    y_velocity = -1 * abs(y_velocity)
                else:
                    # パドル下部
                    collision_distance = self.ball.y - (
                        self.paddle.left_y + self.paddle.height / 2
                    )
                    if collision_distance > self.paddle.height / 2:
                        self.ball.angle = self.ball.bound_angle.get("left_bottom")
                    else:
                        self.ball.angle = (
                            self.ball.bound_angle.get("left_bottom")
                            / (self.paddle.height / 2)
                            * collision_distance
                        )
                    x_velocity *= -1
                    y_velocity = abs(y_velocity)
            elif (
                (
                    self.ball.x + self.ball.radius == self.game_window.width
                    and self.paddle.right_y <= self.ball.y
                    and self.ball.y <= self.paddle.right_y + self.paddle.height
                    and self.ball.direction["facing_right"]
                )
                or (
                    self.ball.x + self.ball.radius
                    >= self.game_window.width - self.paddle.width
                    and self.paddle.right_y + self.paddle.height / 2 >= self.ball.y
                    and self.ball.y >= self.paddle.right_y - self.ball.radius
                    and self.ball.direction["facing_right"]
                )
                or (
                    self.ball.x + self.ball.radius
                    >= self.game_window.width - self.paddle.width
                    and self.paddle.right_y + self.paddle.height / 2 <= self.ball.y
                    and self.ball.y
                    <= self.paddle.right_y + self.paddle.height + self.ball.radius
                    and self.ball.direction["facing_right"]
                )
            ):
                # 右パドルとの衝突
                if self.ball.y <= self.paddle.right_y + self.paddle.height / 2:
                    # パドル上部
                    collision_distance = (
                        self.paddle.right_y + self.paddle.height / 2
                    ) - self.ball.y
                    if collision_distance > self.paddle.height / 2:
                        self.ball.angle = self.ball.bound_angle.get("right_top")
                    else:
                        self.ball.angle = (
                            math.pi
                            + (self.ball.bound_angle["right_top"] - math.pi)
                            / (self.paddle.height / 2)
                            * collision_distance
                        )
                    x_velocity *= -1
                    y_velocity = -1 * abs(y_velocity)
                else:
                    # パドル下部
                    collision_distance = self.ball.y - (
                        self.paddle.right_y + self.paddle.height / 2
                    )
                    if collision_distance > self.paddle.height / 2:
                        self.ball.angle = self.ball.bound_angle.get("right_bottom")
                    else:
                        self.ball.angle = (
                            math.pi
                            - (math.pi - self.ball.bound_angle["right_bottom"])
                            / (self.paddle.height / 2)
                            * collision_distance
                        )
                    x_velocity *= -1
                    y_velocity = abs(y_velocity)

            self.ball.angle = Utils.normalize_angle(self.ball.angle)
            # print("angle: ", self.ball.angle)
            Utils.set_direction(self.ball)
            # ballの位置補正
            if (
                self.ball.x - self.ball.radius > self.paddle.width
                and self.ball.x + x_velocity - self.ball.radius < self.paddle.width
                and self.ball.direction["facing_left"]
            ):
                self.ball.x = self.paddle.width + self.ball.radius
            else:
                self.ball.x += x_velocity
            if (
                self.ball.x + self.ball.radius
                < self.game_window.width - self.paddle.width
                and self.ball.x + x_velocity + self.ball.radius
                > self.game_window.width - self.paddle.width
                and self.ball.direction["facing_right"]
            ):
                self.ball.x = (
                    self.game_window.width - self.paddle.width - self.ball.radius
                )
            else:
                self.ball.y += y_velocity
            if self.ball.y - self.ball.radius < 0:
                self.ball.y = self.ball.radius
            if self.ball.y + self.ball.radius > self.game_window.height:
                self.ball.y = self.game_window.height - self.ball.radius

    async def check_game_state(self):
        if self.ball.x - self.ball.radius > self.game_window.width:
            self.left_score += 1
            self.state = "stop"
        elif self.ball.x + self.ball.radius < 0:
            self.right_score += 1
            self.state = "stop"

    async def connect(self):
        if "game_loop" in self.tasks:
            self.tasks["game_loop"].cancel()
        await self.channel_layer.group_add("sendmessage", self.channel_name)
        print("Websocket connected")
        await self.accept()
        self.tasks["game_loop"] = asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        if "game_loop" in self.tasks:
            self.tasks["game_loop"].cancel()
        await self.channel_layer.group_discard("sendmessage", self.channel_name)
        print("Websocket disconnected")

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        key = data.get("key")
        action = data.get("action")

        async with self.lock:
            if key == "D" and action == "pressed":
                if (
                    self.paddle.left_y + 3
                    <= self.game_window.height - self.paddle.height
                ):
                    self.paddle.left_y += 3
            elif key == "E" and action == "pressed":
                if self.paddle.left_y - 3 >= 0:
                    self.paddle.left_y -= 3
            elif key == "K" and action == "pressed":
                if (
                    self.paddle.right_y + 3
                    <= self.game_window.height - self.paddle.height
                ):
                    self.paddle.right_y += 3
            elif key == "I" and action == "pressed":
                if self.paddle.right_y - 3 >= 0:
                    self.paddle.right_y -= 3

        if self.state == "stop":
            await self.send_pos()

    async def handle_other_message(self, message):
        # その他のメッセージに対応する処理
        print(f"Other message received: {message}")
        response_message = {"message": f"Received: {message}"}
        await self.channel_layer.group_send(
            "sendmessage",
            {
                "type": "send_message",
                "content": response_message,
            },
        )

    async def send_pos(self):
        response_message = {
            "left_paddle_y": self.paddle.left_y,
            "right_paddle_y": self.paddle.right_y,
            "ball_x": self.ball.x,
            "ball_y": self.ball.y,
            "left_score": self.left_score,
            "right_score": self.right_score,
        }
        await self.channel_layer.group_send(
            "sendmessage",
            {
                "type": "send_message",
                "content": response_message,
            },
        )

    async def send_message(self, event):
        # contentの中にある辞書を取り出し
        message = event["content"]
        # 辞書をjson型にする
        await self.send(text_data=json.dumps(message))
