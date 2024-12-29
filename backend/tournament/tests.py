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
            match_number=1,
            timestamp=timezone.now(),
            player1=self.player1,
            player2=self.player2,
            player1_score=0,
            player2_score=0,
        )
        self.assertEqual(match.tournament.name, "Test Tournament")
        self.assertEqual(match.match_number, 1)
        self.assertEqual(match.player1.name, "Player 1")
        self.assertEqual(match.player2.name, "Player 2")

    def test_unique_match_number_constraint(self):
        # 同じトーナメント内で同じマッチ番号を持つ試合を作成しようとするとエラーが発生するか
        Match.objects.create(
            tournament=self.tournament,
            match_number=1,
            timestamp=timezone.now(),
            player1=self.player1,
            player2=self.player2,
        )
        with self.assertRaises(Exception):  # IntegrityErrorが発生するはず
            Match.objects.create(
                tournament=self.tournament,
                match_number=1,
                timestamp=timezone.now(),
                player1=self.player1,
                player2=self.player2,
            )

    def test_winner_calculation(self):
        match = Match.objects.create(
            tournament=self.tournament,
            match_number=1,
            timestamp=timezone.now(),
            player1=self.player1,
            player2=self.player2,
            player1_score=10,
            player2_score=5,
        )
        self.assertEqual(match.winner, self.player1)


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
        self.tournament = Tournament.objects.create(
            name="Test Tournament", date=timezone.now().date()
        )
        self.match = Match.objects.create(
            tournament=self.tournament,
            match_number=1,
            timestamp=timezone.now(),
            player1=self.player1,
            player2=self.player2,
            player1_score=0,
            player2_score=0,
        )
        self.url = reverse("tournament:save-data")
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    def test_get_latest_tournament(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.tournament.id)

    def test_save_match_data(self):
        data = {
            "currentMatchId": 0,
            "tournamentData": {
                "id": self.tournament.id,
                "matches": [
                    {
                        "match_number": 1,
                        "player1": {"id": self.player1.id},
                        "player2": {"id": self.player2.id},
                        "player1_score": 10,
                        "player2_score": 5,
                        "winner": "player1",
                    }
                ],
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_match = Match.objects.get(id=self.match.id)
        self.assertEqual(updated_match.player1_score, 10)
        self.assertEqual(updated_match.player2_score, 5)
        self.assertEqual(updated_match.winner, self.player1)

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
