from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, OTPSerializer, SignUpSerializer
from .utils.auth import JWTAuthentication, generate_jwt


@method_decorator([sensitive_post_parameters(), never_cache], name="dispatch")
class CustomLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user.otp_enabled:
                return Response(
                    {"redirect": "accounts:verify_otp"}, status=status.HTTP_200_OK
                )
            token = generate_jwt(user)
            login(request, user)
            return Response(
                {"token": token, "redirect": "homepage"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response({"redirect": "accounts:login"}, status=status.HTTP_200_OK)


@method_decorator([sensitive_post_parameters(), never_cache], name="dispatch")
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"redirect": "accounts:login"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator([never_cache], name="dispatch")
class SetupOTPView(APIView):
    authentication_classes = [
        JWTAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        user = request.user
        if not TOTPDevice.objects.filter(user=user, confirmed=True).exists():
            device = TOTPDevice.objects.create(user=user, confirmed=False)
            uri = device.config_url
            secret_key = device.bin_key.hex()

            return Response(
                {"otpauth_url": uri, "secret_key": secret_key},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "OTP already set up"}, status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):
        user = request.user
        device = TOTPDevice.objects.filter(user=user).first()
        device.confirmed = True
        user.otp_enabled = True
        device.save()
        user.save()
        return Response({"message": "OTP setup successful"}, status=status.HTTP_200_OK)


@method_decorator([sensitive_post_parameters()], name="dispatch")
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            otp = serializer.validated_data["otp_token"]
            device = TOTPDevice.objects.filter(user=user).first()

            if device and device.verify_token(otp):
                token = generate_jwt(user)
                login(request, user)
                return Response(
                    {"token": token, "redirect": "homepage"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
