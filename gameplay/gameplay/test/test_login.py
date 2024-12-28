from accounts.models import CustomUser
from django.test import TestCase
from django.urls import reverse


class GamePlayViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")  # loginが必要
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    def test_play_game_view(self):
        response = self.client.get(reverse("gameplay:gameplay"))  # ここを修正
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "gameplay/playpage.html")
