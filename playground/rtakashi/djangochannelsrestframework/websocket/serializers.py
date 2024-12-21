from rest_framework import serializers
from .models import GameState


class GameStateSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import GameState

        model = GameState
        fields = ["id", "state", "r_player", "l_player", "ball_x", "ball_y", "r_score", "l_score"]
