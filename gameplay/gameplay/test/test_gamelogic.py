# import time
# import json
# import asyncio
# from channels.testing import WebsocketCommunicator
# from gameplay.PongLogic.consumers import PongLogic
# from django.test import TestCase


# class PongLogicTests(TestCase):
#     # DキーとKキーを30秒押し続けた場合,左のスコア確認
#     async def test_press_d_and_k_key_while_hold(self):
#         consumer = PongLogic()
#         self.assertIsInstance(consumer, PongLogic)
#         communicator = WebsocketCommunicator(PongLogic.as_asgi(), "/ws/gameplay/")

#         connected = await communicator.connect()
#         self.assertTrue(connected)

#         start_time = time.time()
#         duration = 30
#         pre_left = 240
#         pre_right = 240
#         pre_score = 0
#         while time.time() - start_time < duration:
#             await communicator.send_json_to(
#                 {"key": "D", "action": "pressed", "paddle": "left"}
#             )
#             await asyncio.sleep(0.1)
#             await communicator.send_json_to(
#                 {"key": "K", "action": "pressed", "paddle": "right"}
#             )
#             # await asyncio.sleep(0.1)

#             response = await communicator.receive_json_from()
#             self.assertIn("left_paddle_y", response)
#             self.assertIn("right_paddle_y", response)
#             print(response)
#             self.assertGreater(response["left_paddle_y"], pre_left - 1)
#             self.assertGreater(response["right_paddle_y"], pre_right - 1)
#             self.assertLess(
#                 response["left_paddle_y"],
#                 consumer.game_window.height - consumer.paddle.height - 1,
#             )
#             self.assertLess(
#                 response["right_paddle_y"],
#                 consumer.game_window.height - consumer.paddle.height - 1,
#             )
#             pre_left = response["left_paddle_y"]
#             pre_right = response["right_paddle_y"]
#             if consumer.ball.x - consumer.ball.radius > consumer.game_window.width:
#                 printf("left point get")
#                 self.assertGreater(response["left_score"], pre_score)
#                 pre_score = response["left_score"]

#         await communicator.disconnect()

#     # # EキーとIキーを30秒押し続けた場合 右スコア確認
#     async def test_press_e_and_i_key_while_hold(self):
#         consumer = PongLogic()
#         self.assertIsInstance(consumer, PongLogic)
#         communicator = WebsocketCommunicator(PongLogic.as_asgi(), "/ws/gameplay/")

#         connected = await communicator.connect()
#         self.assertTrue(connected)

#         start_time = time.time()
#         duration = 30
#         pre_left = 240
#         pre_right = 240
#         pre_score = 0
#         while time.time() - start_time < duration:
#             await communicator.send_json_to(
#                 {"key": "E", "action": "pressed", "paddle": "left"}
#             )
#             await asyncio.sleep(0.1)
#             await communicator.send_json_to(
#                 {"key": "I", "action": "pressed", "paddle": "right"}
#             )
#             # await asyncio.sleep(0.1)

#             response = await communicator.receive_json_from()
#             self.assertIn("left_paddle_y", response)
#             self.assertIn("right_paddle_y", response)
#             print(response)
#             self.assertLess(response["left_paddle_y"], pre_left + 1)
#             self.assertLess(response["right_paddle_y"], pre_right + 1)
#             self.assertGreater(
#                 response["left_paddle_y"],
#                 0,
#             )
#             self.assertLess(
#                 response["right_paddle_y"],
#                 consumer.game_window.height - consumer.paddle.height - 1,
#             )
#             pre_left = response["left_paddle_y"]
#             pre_right = response["right_paddle_y"]
#             if consumer.ball.x - consumer.ball.radius < 0:
#                 print("right point get")
#                 self.assertGreater(response["right_score"], pre_score)
#                 pre_score = response["right_score"]
#         await communicator.disconnect()
