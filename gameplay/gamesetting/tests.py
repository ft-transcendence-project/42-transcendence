# from django.test import TestCase
# from rest_framework.test import APIClient
# from .models import GameSetting

# class GameSettingViewTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.game_setting = GameSetting.objects.create(
#             ball_velocity="normal",
#             ball_size="normal",
#             map="a"
#         )
#         self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
#         self.client.defaults["wsgi.url_scheme"] = "https"

#     def test_get(self):
#         response = self.client.get("/gameplay/api/gamesetting/", follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(GameSetting.objects.last().ball_velocity, "normal")

#     def test_post(self):
#         data = {
#             "ball_velocity": "fast",
#             "ball_size": "big",
#             "map": "b"
#         }
#         response = self.client.post("/gameplay/api/gamesetting/", data, format='json')
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(GameSetting.objects.count(), 2)
#         self.assertEqual(GameSetting.objects.last().ball_velocity, "fast")

#     def test_put(self):
#         data = {
#             "ball_velocity": "slow",
#             "ball_size": "small",
#             "map": "c"
#         }
#         response = self.client.put(f"/gameplay/api/gamesetting/{self.game_setting.id}/", data, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.game_setting.refresh_from_db()
#         self.assertEqual(self.game_setting.ball_velocity, "slow")

#     def test_delete(self):
#         data = {
#             "ball_velocity": "fast",
#             "ball_size": "big",
#             "map": "b"
#         }
#         response = self.client.post("/gameplay/api/gamesetting/", data, format='json')
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(GameSetting.objects.count(), 2)
#         response = self.client.delete(f"/gameplay/api/gamesetting/{self.game_setting.id}/")
#         self.assertEqual(response.status_code, 204)
#         self.assertEqual(GameSetting.objects.count(), 1)
#         self.assertEqual(GameSetting.objects.last().ball_velocity, "fast")