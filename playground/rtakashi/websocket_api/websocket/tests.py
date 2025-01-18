import asyncio
import json

from channels.testing import WebsocketCommunicator
from django.test import TestCase

from .PongLogic.consumers import PongLogic

# Create your tests here.


class GameOperationApiTests(TestCase):
    async def test_move_player(self):
        self.communicator = WebsocketCommunicator(PongLogic.as_asgi(), "/ws/gamelogic/")
        self.connected = await self.communicator.connect()
        self.assertTrue(self.connected)
        # 右側のパドルを上に動かす
        await self.communicator.send_json_to({"action": "pressed", "key": "I"})
        # 1回目は初期状態のレスポンスが返ってくるため無視
        _ = await self.communicator.receive_json_from()
        response = await self.communicator.receive_json_from()
        self.assertEqual(response["right_paddle_y"], 237)
        # 左側のパドルを上に動かす
        await self.communicator.send_json_to({"action": "pressed", "key": "E"})
        response = await self.communicator.receive_json_from()
        self.assertEqual(response["left_paddle_y"], 237)
        # 右側のパドルを下に動かす
        await self.communicator.send_json_to({"action": "pressed", "key": "K"})
        response = await self.communicator.receive_json_from()
        self.assertEqual(response["right_paddle_y"], 240)
        # 左側のパドルを下に動かす
        await self.communicator.send_json_to({"action": "pressed", "key": "D"})
        response = await self.communicator.receive_json_from()
        self.assertEqual(response["left_paddle_y"], 240)
