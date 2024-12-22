import random

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Match, Player, Tournament
from .serializers import TournamentDetailSerializer
from .serializers import MatchSaveSerializer


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


class SaveScoreView(APIView):
    def post(self, request):
        tournament_data = request.data.get('tournamentData')
        if not tournament_data:
            return Response({"error": "tournamentDataが見つかりません。"}, status=status.HTTP_400_BAD_REQUEST)

        matches = tournament_data.get('matches', [])
        if not matches:
            return Response({"error": "試合データが見つかりません。"}, status=status.HTTP_400_BAD_REQUEST)

        match_data = matches[0]  
        tournament_id = tournament_data.get('id')
        match_id = match_data.get('id')
        match_number = match_data.get('match_number')
        timestamp = match_data.get('timestamp')
        player1_id = match_data['player1']['id']
        player2_id = match_data['player2']['id']
        player1_score = match_data.get('player1_score', 0)
        player2_score = match_data.get('player2_score', 0)
        winner_id = match_data['player1']['id'] if match_data.get('winner') == "player1" else match_data['player2']['id']

        tournament, created = Tournament.objects.get_or_create(
            id=tournament_id,
            defaults={
                'name': f"Tournament {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                'date': timezone.now().date(),
            }
        )

        player1, created = Player.objects.get_or_create(
            id=player1_id,
            defaults={'name': f"Player {player1_id}"}
        )

        player2, created = Player.objects.get_or_create(
            id=player2_id,
            defaults={'name': f"Player {player2_id}"}
        )

        winner, created = Player.objects.get_or_create(
            id=winner_id,
            defaults={'name': f"Player {winner_id}"}
        )

        match, created = Match.objects.get_or_create(
            id=match_id,
            tournament=tournament,
            defaults={
                'match_number': match_number,
                'timestamp': timestamp,
                'player1': player1,
                'player2': player2,
                'player1_score': player1_score,
                'player2_score': player2_score,
                'winner': winner,
            }
        )

        if not created:
            serializer = MatchSaveSerializer(match, data={
                'match_number': match_number,
                'timestamp': timestamp,
                'player1_score': player1_score,
                'player2_score': player2_score,
                'winner': winner.id,
            }, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = MatchSaveSerializer(match)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
