# from accounts.models import CustomUser
# from django.test import TestCase
# from django.urls import reverse
# from django.utils.html import escape


# class HomepageViewTests(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             username="testuser", password="password123"
#         )
#         self.client.login(username="testuser", password="password123")  # loginが必要
#         self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
#         self.client.defaults["wsgi.url_scheme"] = "https"

#     def test_homepage_view(self):
#         response = self.client.get(reverse("homepage"))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "homepage/homepage.html")
#         # ボタンが存在し、正しいURLにリンクしているかどうか
#         self.assertIn(
#             f'onclick="window.location.href=\'{escape(reverse("gameplay:gameplay"))}\'"',
#             response.content.decode(),
#             "1vs1ボタンが正しいURLにリンクしていません",
#         )
#         self.assertIn(
#             f'onclick="window.location.href=\'{escape(reverse("tournament:tournament"))}\'"',
#             response.content.decode(),
#             "1vs1ボタンが正しいURLにリンクしていません",
#         )
