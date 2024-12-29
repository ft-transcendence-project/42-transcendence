from .models import Match

def get_match_data(match_id):
    try:
        match = Match.objects.get(id=match_id)
        print(f"Match data of get_match_data: {match}")  # デバッグ用の出力
        # ブロックチェーン上に保存したいデータのみ取り出す
        winner = match.winner
        loser = match.player1 if winner == match.player2 else match.player2
        data = {
            'winner_id': winner.id,
            'winner_score': max(match.player1_score, match.player2_score),
            'loser_id': loser.id,
            'loser_score': min(match.player1_score, match.player2_score),
        }
        print(f"data of get_match_data: {data}")  # デバッグ用の出力
        return data
    except Match.DoesNotExist:
        return None