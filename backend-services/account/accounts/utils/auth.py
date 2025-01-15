import time

import jwt
from accounts.models import CustomUser
from core.settings import SECRET_KEY
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header


def generate_jwt(user):
    timestamp = int(time.time()) + 60 * 60 * 24 * 7
    return jwt.encode(
        {
            "userid": user.pk,
            "username": user.username,
            "email": user.email,
            "exp": timestamp,
        },
        SECRET_KEY,
    )


class JWTAuthentication(BaseAuthentication):
    keyword = "JWT"
    model = None

    def authenticate(self, request):
        try:
            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != self.keyword.lower().encode():
                return None

            if len(auth) == 1:
                raise exceptions.AuthenticationFailed("Authorization header must contain two parts")
            elif len(auth) > 2:
                raise exceptions.AuthenticationFailed("Invalid authorization header format")

            try:
                jwt = auth[1]
                jwt_info = jwt.decode(jwt, SECRET_KEY, algorithms=["HS256"])
                userid = jwt_info.get("userid")
                if userid is None:
                    raise exceptions.AuthenticationFailed("Token does not contain user ID")

                try:
                    user = CustomUser.objects.get(pk=userid)
                    return (user, jwt)
                except CustomUser.DoesNotExist:
                    raise exceptions.AuthenticationFailed("User not found in database")

            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed("Token has expired")
            except jwt.InvalidTokenError:
                raise exceptions.AuthenticationFailed("Invalid token format")

        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Authentication error: {str(e)}")

    def authentication_header(self, request):
        pass
