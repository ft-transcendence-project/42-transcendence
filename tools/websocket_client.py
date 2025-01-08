import websocket
import json
import ssl
import sys
import tty
import termios
import select

class PaddleControl:
    def __init__(self):
        self.running = True
        self.threads = []  # アクティブなスレッドを追跡
        
    def get_key(self):
        # ターミナルの設定を変更して1文字ずつ読み取り
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            if select.select([sys.stdin], [], [], 0.21)[0]:
                return sys.stdin.read(1)
            return ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def handle_input(self):
        while self.running:
            key = self.get_key().lower()
            print(key)

            if key == '':
                send_delayed_message(ws, 'down', 'stop', 'left')

            # 終了条件
            if key == 'q':
                self.running = False
                break

            if key in ['d']:
                send_delayed_message(ws, 'down', 'start', 'left')

            if key in ['e']:
                send_delayed_message(ws, 'up', 'start', 'left')

            elif key in ['k']:
                send_delayed_message(ws, 'down', 'start', 'right')

            elif key in ['i']:
                send_delayed_message(ws, 'up', 'start', 'right')

    def start(self):
        print("Controls: D/E - Left paddle, I/K - Right paddle, Q - Quit")
        try:
            self.handle_input()
        except KeyboardInterrupt:
            self.running = False
        finally:
            # 全スレッドの終了を待機
            for thread in self.threads:
                thread.join(timeout=1.0)


# 接続するWebSocketのURL
url = "wss://localhost:8443/gameplay.ws/ponglogic/1/"

# JSONデータの送信（3秒待機後に送信）
def send_delayed_message(ws, move_direction, action, side):
    message = {
        "move_direction": move_direction,
        "action": action,
        "side": side
    }
    ws.send(json.dumps(message))

# JSONデータの送信
def on_open(ws):
    print("WebSocket接続が開きました")
    controller = PaddleControl()
    controller.start()

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
