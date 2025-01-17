import logging
import os
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import CustomUser
from accounts.utils.auth import generate_jwt

logger = logging.getLogger("oauth")


@api_view(["GET"])
def oauth_view(request):
    logger.info("Initiating OAuth authorization flow")
    if settings.DEBUG == False:
        redirect_url = f"https://api.intra.42.fr/oauth/authorize?client_id={os.environ.get('UID')}&redirect_uri=https://localhost:8443/42pong.api/account/oauth/callback/&response_type=code"
    else:
        redirect_url = f"https://api.intra.42.fr/oauth/authorize?client_id={os.environ.get('UID')}&redirect_uri=http://localhost:8000/oauth/callback/&response_type=code"
    logger.debug(f"Redirecting to: {redirect_url}")
    return redirect(redirect_url)


@api_view(["GET"])
def oauth_callback_view(request):
    logger.info("Received OAuth callback")
    code = request.GET.get("code")
    error = request.GET.get("error")

    if error:
        logger.error(f"OAuth error: {error} - {request.GET.get('error_description')}")
        return Response(
            {
                "error": error,
                "error_description": request.GET.get("error_description"),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if code:
        logger.debug("Exchanging authorization code for access token")
        if settings.DEBUG == False:
            response = requests.post(
                "https://api.intra.42.fr/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": os.environ.get("UID"),
                    "client_secret": os.environ.get("SECRET"),
                    "code": code,
                    "redirect_uri": "https://localhost:8443/42pong.api/account/oauth/callback/",
                },
            )
        else:
            response = requests.post(
                "https://api.intra.42.fr/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": os.environ.get("UID"),
                    "client_secret": os.environ.get("SECRET"),
                    "code": code,
                    "redirect_uri": "http://localhost:8000/oauth/callback/",
                },
            )
        token_data = response.json()
        access_token = token_data.get("access_token")

        if access_token:
            user_info_response = requests.get(
                "https://api.intra.42.fr/v2/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            user_info = user_info_response.json()
            username = user_info.get("login")
            logger.info(f"Retrieved user info for: {username}")

            user, created = CustomUser.objects.get_or_create(username=username)
            if created:
                logger.info(f"Created new user account for: {username}")
                user.set_unusable_password()
                user.save()

            logger.info(f"Successfully authenticated user: {username}")

            if settings.DEBUG == False and user.otp_enabled:
                params = urlencode({"user": user.username})
                return redirect(f"https://localhost:8443/#/verify-otp?{params}")
            elif user.otp_enabled:
                params = urlencode({"user": user.username})
                return redirect(f"http://localhost:3000/#/verify-otp?{params}")

            if settings.DEBUG == False:
                response = redirect("https://localhost:8443/#/")
            else:
                response = redirect("http://localhost:3000/#/")

            response.set_cookie(
                key="isLoggedIn",
                value="true",
                max_age=86400,
                secure=True,
                samesite="Lax",
            )
            response.set_cookie(
                key="jwt",
                value=generate_jwt(user),
                max_age=86400,
                secure=True,
                httponly=True,
                samesite="Strict",
            )
            return response
    logger.error("No authorization code provided")
    return Response(
        {
            "error": "No code provided",
            "error_description": "Authorization code was not provided or is invalid.",
        },
        status=status.HTTP_400_BAD_REQUEST,
    )
