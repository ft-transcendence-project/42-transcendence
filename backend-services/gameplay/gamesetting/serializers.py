from rest_framework import serializers

from .models import GameSetting


class GameSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSetting
        fields = "__all__"
