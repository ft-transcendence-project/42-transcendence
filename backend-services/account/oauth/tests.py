import os
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
        """OAuth認証ページへのリダイレクトを確認する"""
        response = self.client.get(reverse("oauth:oauth"))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        expected_redirect_uri = (
            "https://localhost:8443/42pong.api/account/oauth/callback/"
            if not settings.DEBUG
            else "http://localhost:8000/oauth/callback/"
        )
        expected_url = (
            f"https://api.intra.42.fr/oauth/authorize?"
            f"client_id={os.environ.get('UID')}&"
            f"redirect_uri={expected_redirect_uri}&"
            f"response_type=code"
        )
        self.assertEqual(response.url, expected_url)


class OAuthCallbackViewTests(APITestCase):
    def setUp(self):
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    @patch("requests.post")
    @patch("requests.get")
    def test_oauth_callback_success_without_otp(self, mock_get, mock_post):
        """OTPが無効な場合のOAuthコールバック成功をテストする"""
        mock_post.return_value.json.return_value = {"access_token": "test_token"}
        mock_get.return_value.json.return_value = {"login": "testuser"}

        response = self.client.get(reverse("oauth:callback"), {"code": "test_code"})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        expected_redirect = (
            "https://localhost:8443/#/"
            if not settings.DEBUG
            else "http://localhost:3000/#/"
        )
        self.assertEqual(response.url, expected_redirect)

        # Cookieの検証
        self.assertIn("isLoggedIn", response.cookies)
        self.assertIn("jwt", response.cookies)
        self.assertEqual(response.cookies["isLoggedIn"].value, "true")

    @patch("requests.post")
    @patch("requests.get")
    def test_oauth_callback_success_with_otp(self, mock_get, mock_post):
        """OTPが有効な場合のOAuthコールバック成功をテストする"""
        user = CustomUser.objects.create_user(username="testuser")
        user.otp_enabled = True
        user.save()

        mock_post.return_value.json.return_value = {"access_token": "test_token"}
        mock_get.return_value.json.return_value = {"login": "testuser"}

        response = self.client.get(reverse("oauth:callback"), {"code": "test_code"})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        expected_redirect = (
            "https://localhost:8443/#/verify-otp"
            if not settings.DEBUG
            else "http://localhost:3000/#/verify-otp"
        )
        self.assertIn(expected_redirect, response.url)
        self.assertIn("user=testuser", response.url)

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
