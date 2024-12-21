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
        tournament_id = request.data.get('tournament_id')
        match_id = request.data.get('id')
        player1_id = request.data.get('player1_id')
        player2_id = request.data.get('player2_id')
        winner_id = request.data.get('winner_id')

        # トーナメントの取得または作成
        if tournament_id:
            tournament, created = Tournament.objects.get_or_create(
                id=tournament_id,
                defaults={
                    'name': f"Tournament {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                    'date': timezone.now().date(),
                }
            )
        else:
            tournament = Tournament.objects.create(
                name=f"Tournament {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                date=timezone.now().date(),
            )

        # プレイヤー1の取得または作成
        player1, created = Player.objects.get_or_create(
            id=player1_id,
            defaults={'name': f"Player {player1_id}"}
        )

        # プレイヤー2の取得または作成
        player2, created = Player.objects.get_or_create(
            id=player2_id,
            defaults={'name': f"Player {player2_id}"}
        )

        # 勝者の取得
        winner = None
        if winner_id:
            winner, created = Player.objects.get_or_create(
                id=winner_id,
                defaults={'name': f"Player {winner_id}"}
            )

        # マッチの取得または作成
        if match_id:
            match, created = Match.objects.get_or_create(
                id=match_id,
                tournament=tournament,
                defaults={
                    'match_number': request.data.get('match_number', 1),
                    'timestamp': request.data.get('timestamp', timezone.now()),
                    'player1': player1,
                    'player2': player2,
                    'player1_score': request.data.get('player1_score', 0),
                    'player2_score': request.data.get('player2_score', 0),
                    'winner': winner,
                }
            )
            if not created:
                # 既存のマッチがある場合は更新
                serializer = MatchSaveSerializer(match, data=request.data, partial=True)
        else:
            # 新規マッチの作成
            serializer = MatchSaveSerializer(data=request.data)

        # シリアライザのバリデーションと保存
        if serializer.is_valid():
            serializer.save(
                tournament=tournament,
                player1=player1,
                player2=player2,
                winner=winner,
                match_number=request.data.get('match_number', 1),
                timestamp=request.data.get('timestamp', timezone.now()),
                player1_score=request.data.get('player1_score', 0),
                player2_score=request.data.get('player2_score', 0)
            )
            return Response(serializer.data, status=status.HTTP_200_OK if match_id else status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
