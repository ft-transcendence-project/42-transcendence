from .services import get_match_data
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../blockchain')))
from web3_ganache_connect import TournamentContract

def record_match_on_blockchain(winner_id, winner_score, loser_id, loser_score):
    try:
        tournament = TournamentContract()
        receipt = tournament.record_match(
            winner_id,
            winner_score,
            loser_id,
            loser_score
        )
        print(f"Transaction receipt: {receipt}")
        return receipt
    except Exception as e:
        print(f"An eror occurred while recording match on blockchain: {e}")
