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


# DBへの保存処理を行うシリアライザ
class MatchSaveSerializer(serializers.ModelSerializer):
    tournament_id = serializers.PrimaryKeyRelatedField(queryset=Tournament.objects.all(), source='tournament')
    player1_id = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), source='player1')
    player2_id = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), source='player2')
    winner_id = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), source='winner')

    class Meta:
        model = Match
        fields = [
            "id",
            "tournament_id",
            "match_number",
            "timestamp",
            "player1_id",
            "player2_id",
            "player1_score",
            "player2_score",
            "winner_id",
        ]


class TournamentDetailSerializer(serializers.ModelSerializer):
    matches = MatchDetailSerializer(source="match_set", many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = ["id", "name", "date", "matches"]
