from unittest.mock import patch

from accounts.models import CustomUser
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class OAuthViewTests(APITestCase):
    def setUp(self):
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    def test_oauth_view_redirect(self):
        """OAuth認証ページにリダイレクトされることを確認する"""
        response = self.client.get(reverse("oauth:oauth"))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("https://api.intra.42.fr/oauth/authorize", response.url)


class OAuthCallbackViewTests(APITestCase):
    def setUp(self):
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    @patch("requests.post")
    @patch("requests.get")
    def test_oauth_callback_view_success(self, mock_get, mock_post):
        """OAuthコールバックが成功し、ユーザーが作成されログインされることを確認する"""
        mock_post.return_value.json.return_value = {"access_token": "test_token"}
        mock_get.return_value.json.return_value = {"login": "testuser"}

        response = self.client.get(reverse("oauth:callback"), {"code": "test_code"})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        if settings.DEBUG == False:
            self.assertEqual(response.url, "https://localhost:8443/#/")
        else:
            self.assertEqual(response.url, "http://localhost:3000/#/")

        user = CustomUser.objects.get(username="testuser")
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)

    def test_oauth_callback_view_error(self):
        """エラーが発生した場合、エラーメッセージが返されることを確認する"""
        response = self.client.get(
            reverse("oauth:callback"),
            {"error": "access_denied", "error_description": "Access was denied"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "error": "access_denied",
                "error_description": "Access was denied",
            },
        )

    def test_oauth_callback_view_no_code(self):
        """コードが提供されていない場合、エラーメッセージが返されることを確認する"""
        response = self.client.get(reverse("oauth:callback"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "error": "No code provided",
                "error_description": "Authorization code was not provided or is invalid.",
            },
        )
