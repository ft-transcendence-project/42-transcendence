import websocket
import json
import ssl
import time
import threading

# 接続するWebSocketのURL
url = "wss://localhost:8443/gameplay.ws/ponglogic/1/"

# JSONデータの送信（3秒待機後に送信）
def send_delayed_message(ws):
    time.sleep(3)  # 3秒待機
    print("3秒待機後にデータを送信します")
    message = {
        "move_direction": "down",
        "action": "start",
        "side": "left"
    }
    ws.send(json.dumps(message))

# JSONデータの送信
def on_open(ws):
    print("WebSocket接続が開きました")
    # 新しいスレッドで送信を実行
    threading.Thread(target=send_delayed_message, args=(ws,)).start()

# メッセージ受信時の処理
def on_message(ws, message):
    pass
    # print("受信したメッセージ:", message)
    # try:
    #     data = json.loads(message)  # JSONとしてパース
    #     print("パースしたJSONデータ:", data)
	# except json.JSONDecodeError:
    #     print("JSONデータのパースに失敗しました")

# エラー時の処理
def on_error(ws, error):
    print("エラーが発生しました:", error)

# 接続が閉じられたときの処理
def on_close(ws, close_status_code, close_msg):
    print("WebSocket接続が閉じられました")

# WebSocketの設定と接続
websocket.enableTrace(False)  # デバッグ情報を出力
ws = websocket.WebSocketApp(
    url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)

# WebSocketのイベントループを開始
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
