from .services import get_match_data
from blockchain import web3_ganache_connect

def record_match_on_blockchain(match_id):
    match_data = get_match_data(match_id)
    if not match_data:
        print(f"Match data not found for match_id: {match_id}")
        return

    try:
        tournament = web3_ganache_connect.TournamentContract
        receipt = tournament.record_match(
            match_data['winner_id'],
            match_data['winner_score'],
            match_data['loser_id'],
            match_data['loser_score']
        )
        print(f"Transaction receipt: {receipt}")
    except Exception as e:
        print(f"An eror occurred while recording match on blockchain: {e}")