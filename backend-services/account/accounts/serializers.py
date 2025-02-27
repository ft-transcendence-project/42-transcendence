from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError("Invalid username or password")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'")

        data["user"] = user
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "password", "email", "default_language"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
            default_language=validated_data.get("default_language", "en"),
        )
        return user


class OTPSerializer(serializers.Serializer):
    otp_token = serializers.CharField(max_length=6)

    def validate(self, data):
        request = self.context.get("request")
        username = request.GET.get("user")

        if not username:
            raise serializers.ValidationError("Username is required")

        try:
            user = CustomUser.objects.get(username=username)
            data["user"] = user
            return data
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
