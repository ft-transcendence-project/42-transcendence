from rest_framework import serializers

from .models import Match, Player, Tournament


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "name"]


class MatchDetailSerializer(serializers.ModelSerializer):
    player1 = PlayerSerializer()
    player2 = PlayerSerializer()
    winner = PlayerSerializer()

    class Meta:
        model = Match
        fields = [
            "id",
            "match_number",
            "timestamp",
            "player1",
            "player2",
            "player1_score",
            "player2_score",
            "winner",
        ]


class TournamentDetailSerializer(serializers.ModelSerializer):
    matches = MatchDetailSerializer(source="match_set", many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = ["id", "name", "date", "matches"]
