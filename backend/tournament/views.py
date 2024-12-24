import random

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Match, Player, Tournament
from .serializers import MatchDetailSerializer, TournamentDetailSerializer


class TournamentRegisterView(APIView):
    def post(self, request):
        player_names = request.data
        if len(player_names) != 8:
            return Response(
                {"error": "Require 8 players"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tournament = Tournament.objects.create(
                name=f"Tournament {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                date=timezone.now().date(),
            )

            players = [Player.objects.create(name=name) for name in player_names]
            random.shuffle(players)

            for i in range(4):
                Match.objects.create(
                    tournament=tournament,
                    match_number=i + 1,
                    timestamp=timezone.now(),
                    player1=players[i * 2],
                    player2=players[i * 2 + 1],
                    player1_score=0,
                    player2_score=0,
                )

            serializer = TournamentDetailSerializer(tournament)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SaveDataView(APIView):
    def get(self, request):
        try:
            latest_tournament = Tournament.objects.latest("date")
            serializer = TournamentDetailSerializer(latest_tournament)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Tournament.DoesNotExist:
            return Response(
                {"error": "No tournament found"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        tournament_data = request.data.get("tournamentData")
        if not tournament_data:
            return Response(
                {"error": "Tournament data not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        matches = tournament_data.get("matches")
        if not matches:
            return Response(
                {"error": "Matches data not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        match_id = request.data.get("currentMatch_id")
        if match_id is None:
            return Response(
                {"error": "Current match id not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        match_data = matches[match_id]

        try:
            match = Match.objects.get(
                tournament_id=tournament_data.get("id"),
                match_number=match_data.get("match_number"),
            )

            # 既存のマッチを更新
            match.player1_score = match_data.get("player1_score", 0)
            match.player2_score = match_data.get("player2_score", 0)
            match.winner = Player.objects.get(
                id=(
                    match_data["player1"]["id"]
                    if match_data.get("winner") == "player1"
                    else match_data["player2"]["id"]
                )
            )
            match.save()

            serializer = MatchDetailSerializer(match)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found"}, status=status.HTTP_404_NOT_FOUND
            )
