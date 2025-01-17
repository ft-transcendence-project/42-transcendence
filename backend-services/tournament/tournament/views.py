import logging
import random

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Match, Player, Tournament
from .serializers import MatchDetailSerializer, TournamentDetailSerializer

from .web3_ganache_connect import record_match_on_blockchain
logger = logging.getLogger("tournament")


class TournamentRegisterView(APIView):
    def post(self, request):
        logger.info("Attempting to create new tournament with players")
        player_names = request.data
        if len(player_names) != 8:
            logger.error(f"Invalid number of players: {len(player_names)}")
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
            logger.info(
                f"Successfully created tournament {tournament.id} with {len(players)} players"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Failed to create tournament: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SaveDataView(APIView):
    def get(self, request, pk=None):
        logger.info(f"Retrieving tournament data for id: {pk}")
        try:
            latest_tournament = Tournament.objects.get(id=pk)
            serializer = TournamentDetailSerializer(latest_tournament)
            logger.info(f"Successfully retrieved tournament {pk}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Tournament.DoesNotExist:
            logger.error(f"Tournament not found with id: {pk}")
            return Response(
                {"error": "No tournament found"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk=None):
        logger.info(f"Updating match data for tournament {pk}")
        match_data = request.data.get("currentMatch")
        if not match_data:
            logger.error("No match data provided in request")
            return Response(
                {"error": "No match data provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            match = Match.objects.get(
                tournament_id=pk,
                match_number=match_data.get("match_number"),
                round=match_data.get("round"),
            )

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

            #ブロックチェーンに試合結果を記録
            try:
                receipt = record_match_on_blockchain(
                    tournament_id=pk,
                    round=match.round,
                    match_number=match.match_number,
                    timestamp=int(match.timestamp.timestamp()),
                    player1_id=match.player1.id,
                    player2_id=match.player2.id,
                    player1_score=match.player1_score,
                    player2_score=match.player2_score
                )
                print(f"Blockchain transaction receipt: {receipt}")
            except Exception as e:
                return Response(
                    {"error": f"An error occurred while recording match on blockchain: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            current_round_matches = Match.objects.filter(
                tournament_id=pk,
                round=match.round,
            )

            logger.info(
                f"Successfully updated match {match.match_number} in tournament {pk}"
            )

            if all(m.winner for m in current_round_matches):
                if len(current_round_matches) >= 2:
                    logger.info(f"Creating next round matches for tournament {pk}")
                    self.create_next_matches(pk, current_round_matches, match.round)
                else:
                    logger.info(
                        f"Tournament {pk} completed. Winner: {match.winner.name}"
                    )
                    tournament = Tournament.objects.get(id=pk)
                    tournament.is_over = True
                    tournament.winner = match.winner
                    tournament.save()
                    return Response(
                        {
                            "match": MatchDetailSerializer(match).data,
                            "tournament_complete": True,
                            "winner": match.winner.name,
                        },
                        status=status.HTTP_200_OK,
                    )

            serializer = MatchDetailSerializer(match)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Match.DoesNotExist:
            logger.error(f"Match not found in tournament {pk}")
            return Response(
                {"error": "Match not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create_next_matches(self, tournament_id, current_round_matches, current_round):
        # (round, match_number) = (1, 1), (1, 2) , ... ,(3, 1)
        logger.info(
            f"Creating next round matches for tournament {tournament_id}, round {current_round + 1}"
        )
        next_match_number = 1

        for i in range(0, len(current_round_matches), 2):
            if i + 1 < len(current_round_matches):
                Match.objects.create(
                    tournament_id=tournament_id,
                    match_number=next_match_number,
                    round=current_round + 1,
                    timestamp=timezone.now(),
                    player1=current_round_matches[i].winner,
                    player2=current_round_matches[i + 1].winner,
                    player1_score=0,
                    player2_score=0,
                )
                next_match_number += 1
