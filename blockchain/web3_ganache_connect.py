from web3 import Web3
import json
import os

# Ganacheのサービスに接続
ganache_url = "http://ganache:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# 接続確認
if web3.is_connected():
    print("Successfully connected to Ganache")
else:
    print("Failed to connect to Ganache")

# アカウントと秘密鍵の設定(将来的に自動でとってこれるようにしたい)
account_0 = web3.to_checksum_address('0xdE0C1d0ac10c94c344AB5ebA66f5B685c4C9a18c')
private_key = '0xc90093bb19a01812b75ccf5fe1288f7689ab5c304179f76f232c1baa7f4148b4'

# デプロイされたコントラクトのアドレスを取得
contract_address = "0x73Be9c27bda8E9dD9fFd9913d79302bc15c4D5CF"

abi_path = "blockchain/truffle/build/contracts/Tournament.json"

# ファイルの存在確認
if not os.path.exists(abi_path):
    raise FileNotFoundError(f"指定されたファイルが見つかりません: {abi_path}")

try:
    with open(abi_path, 'r') as f:
        contract_json = json.load(f)  # JSONファイルを読み込む
except json.JSONDecodeError as e:
    raise ValueError(f"JSONの読み込みに失敗しました: {e}")

# 'abi'キーの存在確認
if 'abi' not in contract_json:
    raise KeyError("'abi'キーがJSON内に存在しません")

abi = contract_json['abi']  # コントラクトのABIを取得

# デプロイされたコントラクトのインスタンスを作成
tournament = web3.eth.contract(address=contract_address, abi=abi)
print(f"Contract instance created: {tournament}")

# Djangoからコントラクトを操作する関数を定義
# 例: 新しい試合結果を記録する
def record_match(winner_id, winner_score, loser_id, loser_score):
    nonce = web3.eth.get_transaction_count(account_0)
    transaction = tournament.functions.recordMatch(
        winner_id,
        winner_score,
        loser_id,
        loser_score
    ).build_transaction({
        'from': account_0,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei')
    })
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt

# 例: 特定の試合結果を取得する
def get_match(match_number):
    return tournament.functions.getMatch(match_number).call()

# 新しい試合結果を記録する
receipt = record_match(1, 10, 2, 5)
receipt2 = record_match(3, 8, 4, 3)

# 特定の試合結果を取得する
match_number = 1
match_data = get_match(match_number)
print(f"Match data: {match_data}")