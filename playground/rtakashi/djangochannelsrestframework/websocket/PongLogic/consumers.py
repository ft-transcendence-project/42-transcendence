import json

from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import math
from .utils import Utils
from .shared import SharedState
from .serverside_pong_api import move_paddle, init_game, pause_game, resume_game, set_game_state
from websocket.models import GameState
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from websocket.serializers import GameStateSerializer
from djangochannelsrestframework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    PatchModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DeleteModelMixin,
)
from asgiref.sync import sync_to_async
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import model_observer

class GameStateConsumer(SharedState,GenericAsyncAPIConsumer, ListModelMixin):
    from websocket.models import GameState
    queryset = GameState.objects.all()
    serializer_class = GameStateSerializer
    lookup_field = 'id' 
    # ↑試合番号とか？
    
    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        valid_actions = [
            "move_up",
            "move_down",
            "init_game",
            "pause_game",
            "resume_game",
            "get_game_state"
        ]
        if action not in valid_actions:
            error_response = {
                "error": f"Invalid action: {action}",
                "valid_actions": valid_actions,
            }
            await self.send_json(error_response)
            return
        async with SharedState.lock:
            if action == "get_game_state":
                game_state = await database_sync_to_async(GameState.objects.last)()
                if game_state:
                # シリアライズして返す
                    serialized_data = {
                        "id": game_state.id,
                        "state": game_state.state,
                        "r_player": game_state.r_player,
                        "l_player": game_state.l_player,
                        "ball_x": game_state.ball_x,
                        "ball_y": game_state.ball_y,
                        "r_score": game_state.r_score,
                        "l_score": game_state.l_score,
                    }
                #     serialized_data = self.get_serializer(game_state).data
                    await self.send_json(serialized_data)
                # else:
                #     await self.send_json({"error": "No game state available"})
                # return
                    # await self.game_state_activity.subscribe()
                    print(f"get_state:",game_state)
                    return
            if action == "move_up" or action == "move_down":
                game_state = await move_paddle(action, content)
            elif action == "init_game":
                game_state = await init_game()
            elif action == "pause_game":
                game_state = await pause_game()
            elif action == "resume_game":
                game_state = await resume_game()
            print(f"gamestate2",game_state)
            response_message = Utils.create_game_update_message(SharedState.Ball, SharedState.Paddle, SharedState.Score)
            await self.channel_layer.group_send(
                "sendmessage",
                {
                    "type": "send_message",
                    "content": response_message,
                },
            )
            if action == "init_game":
                await asyncio.sleep(2)
            

class PongLogic(SharedState, AsyncWebsocketConsumer):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.state = "stop" 
        return cls._instance

    async def game_loop(self):
        turn_count = 0
        while SharedState.Score.left < 15 and SharedState.Score.right < 15:
            async with SharedState.lock:
                if self.state == "stop":
                    SharedState.reset_ball_position()
                    SharedState.reset_ball_angle()
                    if turn_count % 2 == 0:
                        SharedState.Ball.angle += math.pi
                    SharedState.Ball.angle = Utils.normalize_angle(SharedState.Ball.angle)
                    turn_count += 1
                    Utils.set_direction(SharedState.Ball)
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
        async with SharedState.lock:
            # self.ball.angle = math.pi / 3 #test用
            velocity = {
                "x": SharedState.Ball.velocity * math.cos(SharedState.Ball.angle),
                "y": SharedState.Ball.velocity * math.sin(SharedState.Ball.angle),
            }
            # 上下の壁衝突判定
            if (
                Utils.has_collided_with_wall(SharedState.Ball, SharedState.GameWindow)
                == True
            ):
                velocity["y"] *= -1
                SharedState.Ball.angle = 2 * math.pi - SharedState.Ball.angle
                SharedState.Ball.angle = Utils.normalize_angle(SharedState.Ball.angle)
                Utils.set_direction(SharedState.Ball)

            # 左パドル衝突判定
            if (
                Utils.has_collided_with_paddle_left(
                    SharedState.Ball, SharedState.Paddle
                )
                == True
            ):
                is_left = True
                # 左パドル上部の衝突判定
                if (
                    Utils.has_collided_with_paddle_top(
                        SharedState.Ball, SharedState.Paddle, is_left
                    )
                    == True
                ):
                    is_top = True
                else:
                    is_top = False
                Utils.update_ball_angle(
                    SharedState.Ball, SharedState.Paddle, is_left, is_top
                )
                velocity["x"], velocity["y"] = Utils.update_ball_velocity(
                    is_top, velocity
                )
            # 右パドル衝突判定
            elif (
                Utils.has_collided_with_paddle_right(
                    SharedState.Ball, SharedState.Paddle, SharedState.GameWindow
                )
                == True
            ):
                is_left = False
                # 右パドル上部衝突判定
                if (
                    Utils.has_collided_with_paddle_top(
                        SharedState.Ball, SharedState.Paddle, is_left
                    )
                    == True
                ):
                    is_top = True
                else:
                    is_top = False
                Utils.update_ball_angle(
                    SharedState.Ball, SharedState.Paddle, is_left, is_top
                )
                velocity["x"], velocity["y"] = Utils.update_ball_velocity(
                    is_top, velocity
                )
            SharedState.Ball.angle = Utils.normalize_angle(SharedState.Ball.angle)
            Utils.set_direction(SharedState.Ball)
            Utils.adjust_ball_position(
                SharedState.Ball, SharedState.Paddle, velocity, SharedState.GameWindow
            )
            await set_game_state("playing")

    async def check_game_state(self):
        async with SharedState.lock:
            if (
                SharedState.Ball.x - SharedState.Ball.radius
                > SharedState.GameWindow.width
            ):
                SharedState.Score.left += 1
                self.state = "stop"
            elif SharedState.Ball.x + SharedState.Ball.radius < 0:
                SharedState.Score.right += 1
                self.state = "stop"
            await set_game_state("playing")

    async def connect(self):
        if "game_loop" in SharedState.tasks:
            SharedState.tasks["game_loop"].cancel()
        await self.channel_layer.group_add("sendmessage", self.channel_name)
        print("Websocket connected")
        await self.accept()
        self.state = "stop"
        SharedState.tasks["game_loop"] = asyncio.create_task(Utils.game_start(self.game_loop()))
        await set_game_state("playing")
    
    async def disconnect(self, close_code):
        if "game_loop" in SharedState.tasks:
            SharedState.init()
            SharedState.tasks["game_loop"].cancel()
            await set_game_state("waiting")
        await self.channel_layer.group_discard("sendmessage", self.channel_name)
        print("Websocket disconnected")

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        key = data.get("key")
        action = data.get("action")

        async with SharedState.lock:
            if key == "D" and action == "pressed":
                if (
                    SharedState.Paddle.left_y + 3
                    <= SharedState.GameWindow.height - SharedState.Paddle.height
                ):
                    SharedState.Paddle.left_y += 3
            elif key == "E" and action == "pressed":
                if SharedState.Paddle.left_y - 3 >= 0:
                    SharedState.Paddle.left_y -= 3
            elif key == "K" and action == "pressed":
                if (
                    SharedState.Paddle.right_y + 3
                    <= SharedState.GameWindow.height - SharedState.Paddle.height
                ):
                    SharedState.Paddle.right_y += 3
            elif key == "I" and action == "pressed":
                if SharedState.Paddle.right_y - 3 >= 0:
                    SharedState.Paddle.right_y -= 3
            await set_game_state("playing")
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
        response_message = Utils.create_game_update_message(SharedState.Ball, SharedState.Paddle, SharedState.Score)
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
