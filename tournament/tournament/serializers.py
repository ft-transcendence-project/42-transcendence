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
            "round",
            "match_number",
            "timestamp",
            "player1",
            "player2",
            "player1_score",
            "player2_score",
            "winner",
        ]


class TournamentDetailSerializer(serializers.ModelSerializer):
    matches = MatchDetailSerializer(many=True, read_only=True)
    winner = PlayerSerializer(read_only=True)

    class Meta:
        model = Tournament
        fields = ["id", "name", "date", "matches", "is_over", "winner"]
