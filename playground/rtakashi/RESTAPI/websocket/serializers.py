from django.contrib.auth.models import Group, User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


# 以下を追加
from rest_framework import serializers

from .models import GameState


class GameStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameState
        fields = ["id", "status"]
