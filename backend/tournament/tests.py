from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Match, Player, Tournament


class ModelTests(TestCase):
    def setUp(self):
        # test用のトーナメントとプレイヤーを作成
        self.tournament = Tournament.objects.create(
            name="Test Tournament", date=timezone.now().date()
        )
        self.player1 = Player.objects.create(name="Player 1")
        self.player2 = Player.objects.create(name="Player 2")

    def test_tournament_creation(self):
        # トーナメントが正しく作成されるか
        self.assertEqual(self.tournament.name, "Test Tournament")

    def test_player_creation(self):
        # プレイヤーが正しく作成されるか
        self.assertEqual(self.player1.name, "Player 1")
        self.assertEqual(self.player2.name, "Player 2")

    def test_match_creation(self):
        # マッチが正しく作成され,トーナメントと関連付けられているか
        match = Match.objects.create(
            tournament=self.tournament,
            round=1,
            match_number=1,
            timestamp=timezone.now(),
            player1=self.player1,
            player2=self.player2,
            player1_score=0,
            player2_score=0,
        )
        self.assertEqual(match.tournament.name, "Test Tournament")
        self.assertEqual(match.round, 1)
        self.assertEqual(match.match_number, 1)
        self.assertEqual(match.player1.name, "Player 1")
        self.assertEqual(match.player2.name, "Player 2")

    def test_unique_match_number_constraint(self):
        # 同じトーナメント内で同じマッチ番号を持つ試合を作成しようとするとエラーが発生するか
        Match.objects.create(
            tournament=self.tournament,
            round=1,
            match_number=1,
            timestamp=timezone.now(),
            player1=self.player1,
            player2=self.player2,
        )
        with self.assertRaises(Exception):  # IntegrityErrorが発生するはず
            Match.objects.create(
                tournament=self.tournament,
                round=1,
                match_number=1,
                timestamp=timezone.now(),
                player1=self.player1,
                player2=self.player2,
            )

    def test_winner_property(self):
        match = Match.objects.create(
            tournament=self.tournament,
            round=1,
            match_number=1,
            timestamp=timezone.now(),
            player1=self.player1,
            player2=self.player2,
            player1_score=0,
            player2_score=0,
        )
        # Initial state
        self.assertIsNone(match.winner)

        # Player 1 wins
        match.player1_score = 10
        match.player2_score = 5
        self.assertEqual(match.winner, self.player1)

        # Player 2 wins
        match.player1_score = 5
        match.player2_score = 10
        self.assertEqual(match.winner, self.player2)


class TournamentRegisterViewTests(APITestCase):
    def setUp(self):
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    def test_successful_tournament_registration(self):
        # 8人のプレイヤー名リストを作成
        player_names = [f"Player {i}" for i in range(1, 9)]
        url = reverse("tournament:tournament-register")  # URLの設定が必要

        # APIエンドポイントにPOSTリクエストを送信
        response = self.client.post(url, player_names, format="json")

        # レスポンスの検証
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tournament.objects.count(), 1)
        self.assertEqual(Player.objects.count(), 8)
        self.assertEqual(Match.objects.count(), 4)

        # 各マッチのスコアと選手の確認
        tournament = Tournament.objects.first()
        matches = Match.objects.filter(tournament=tournament)
        for match in matches:
            self.assertEqual(match.player1_score, 0)
            self.assertEqual(match.player2_score, 0)
            self.assertIsNotNone(match.player1)
            self.assertIsNotNone(match.player2)

    def test_invalid_player_count(self):
        # 7人のプレイヤー名リスト（不正なケース）
        player_names = [f"Player {i}" for i in range(1, 8)]
        url = reverse("tournament:tournament-register")

        response = self.client.post(url, player_names, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Tournament.objects.count(), 0)
        self.assertEqual(Player.objects.count(), 0)


class SaveDataViewTest(APITestCase):
    def setUp(self):
        self.player1 = Player.objects.create(name="Player 1")
        self.player2 = Player.objects.create(name="Player 2")
        self.player3 = Player.objects.create(name="Player 3")
        self.player4 = Player.objects.create(name="Player 4")
        self.tournament = Tournament.objects.create(
            name="Test Tournament", date=timezone.now().date()
        )

        # Create first round matches
        self.match1 = Match.objects.create(
            tournament=self.tournament,
            round=1,
            match_number=1,
            timestamp=timezone.now(),
            player1=self.player1,
            player2=self.player2,
            player1_score=0,
            player2_score=0,
        )
        self.match2 = Match.objects.create(
            tournament=self.tournament,
            round=1,
            match_number=2,
            timestamp=timezone.now(),
            player1=self.player3,
            player2=self.player4,
            player1_score=0,
            player2_score=0,
        )
        self.url = reverse("tournament:save-data")
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

        # Add more players for testing multiple rounds
        self.player5 = Player.objects.create(name="Player 5")
        self.player6 = Player.objects.create(name="Player 6")
        self.player7 = Player.objects.create(name="Player 7")
        self.player8 = Player.objects.create(name="Player 8")

        # Create additional first round matches
        self.match3 = Match.objects.create(
            tournament=self.tournament,
            round=1,
            match_number=3,
            timestamp=timezone.now(),
            player1=self.player5,
            player2=self.player6,
            player1_score=0,
            player2_score=0,
        )
        self.match4 = Match.objects.create(
            tournament=self.tournament,
            round=1,
            match_number=4,
            timestamp=timezone.now(),
            player1=self.player7,
            player2=self.player8,
            player1_score=0,
            player2_score=0,
        )

    def test_get_latest_tournament(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.tournament.id)

    def test_save_match_data_and_create_next_round(self):
        # Save first round matches results
        for i, (match, player) in enumerate(
            [
                (self.match1, self.player1),
                (self.match2, self.player3),
                (self.match3, self.player5),
                (self.match4, self.player7),
            ]
        ):
            data = {
                "currentMatchId": i,
                "tournamentData": {
                    "id": self.tournament.id,
                    "matches": [None] * i
                    + [
                        {
                            "match_number": match.match_number,
                            "round": 1,
                            "player1": {"id": match.player1.id},
                            "player2": {"id": match.player2.id},
                            "player1_score": 10,
                            "player2_score": 5,
                            "winner": "player1",
                        }
                    ],
                },
            }
            response = self.client.post(self.url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if round 2 matches were created
        next_round_matches = Match.objects.filter(tournament=self.tournament, round=2)
        self.assertEqual(next_round_matches.count(), 2)

        # Verify player assignments in round 2
        match1 = next_round_matches.get(match_number=1)
        match2 = next_round_matches.get(match_number=2)

        self.assertEqual(match1.player1, self.player1)  # Winner of match 1
        self.assertEqual(match1.player2, self.player3)  # Winner of match 2
        self.assertEqual(match2.player1, self.player5)  # Winner of match 3
        self.assertEqual(match2.player2, self.player7)  # Winner of match 4

    def test_invalid_tournament_data(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_match_not_found(self):
        data = {
            "currentMatchId": 0,
            "tournamentData": {
                "id": 999,
                "matches": [
                    {
                        "match_number": 999,
                        "player1": {"id": self.player1.id},
                        "player2": {"id": self.player2.id},
                        "player1_score": 10,
                        "player2_score": 5,
                    }
                ],
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
