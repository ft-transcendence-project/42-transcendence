import websocket
import json
import ssl
import sys
import tty
import termios
import select

base_url = "wss://localhost:8443/gameplay.ws/ponglogic/"
def print_colored_message(color, message):
    if color == "white":
        print(message)
    elif color == "red":
        print(f"\033[31m{message}\033[37m")
    elif color == "green":
        print(f"\033[32m{message}\033[37m")
    elif color == "yellow":
        print(f"\033[33m{message}\033[37m")
    elif color == "blue":
        print(f"\033[34m{message}\033[37m")

    

class PaddleControl:
    def __init__(self, paddle_side):
        self.running = True
        self.paddle_side = paddle_side
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

    def handle_input(self, ws):
        while self.running:
            key = self.get_key().lower()
            # print(key)

            if key == '':
                send_delayed_message(ws, 'down', 'stop', 'left')

            # 終了条件
            if key == 'q':
                self.running = False
                ws.close()
                break

            if self.paddle_side == 'left':
                if key in ['d']:
                    send_delayed_message(ws, 'down', 'start', 'left')
    
                if key in ['e']:
                    send_delayed_message(ws, 'up', 'start', 'left')

            if self.paddle_side == 'right':
                if key in ['k']:
                    send_delayed_message(ws, 'down', 'start', 'right')
    
                if key in ['i']:
                    send_delayed_message(ws, 'up', 'start', 'right')

    def start(self, ws):
        if self.paddle_side == 'left':
            print_colored_message("white", "Controls: D - down, E - up, Q - Quit")
        elif self.paddle_side == 'right':
            print_colored_message("white", "Controls: K - down, I - up, Q - Quit")
        try:
            self.handle_input(ws)
        except KeyboardInterrupt:
            self.running = False

# JSONデータの送信（3秒待機後に送信）
def send_delayed_message(ws, move_direction, action, side):
    message = {
        "move_direction": move_direction,
        "action": action,
        "side": side
    }
    ws.send(json.dumps(message))

# JSONデータの送信
def on_open(ws, controller):
    print_colored_message("green", "Connecttion Success!\n")
    controller.start(ws)

# メッセージ受信時の処理
def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get('game_over'):
            print_colored_message("green", "Game over!\n")
            ws.close()
    except json.JSONDecodeError:
        print_colored_message("red", "Error for data\n")

# エラー時の処理
def on_error(ws, error):
    print_colored_message("red", "Error for websocket: " + error + "\n")

# 接続が閉じられたときの処理
def on_close(ws, close_status_code, close_msg):
    print_colored_message("red", "Disconnected\n")

def create_ws_app(url, controller):
    def on_open_wrapperr(ws):
        on_open(ws, controller)

    return websocket.WebSocketApp(
        url,
        on_open=on_open_wrapperr,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

def main():
    print_colored_message("green", "Welcome to Pong Game!!!\n")
    print_colored_message("green", "Please type game id you want to play. ")
    while (True):
        game_id = sys.stdin.readline().strip()
        if game_id.isnumeric():
            url = base_url + game_id + "/"
            break
        else:
            print_colored_message("red", "Invalid input. Please type a number. ")

    print_colored_message("yellow", f"\nOK. The Game id is \n\n\" ----- " + game_id + " ----- \"\n")

    print_colored_message("green", "Which paddle do you want to control?\nType D(Left) or K(Right)")

    while (True):
        user_input = sys.stdin.readline().strip()
        print(user_input)
        if user_input in ['D', 'd']:
            paddle_side = 'left'
            break
        elif user_input in ['K', 'k']:
            paddle_side = 'right'
            break
        else:
            print_colored_message("red", "Invalid input. Please type D(Left) or K(Right).")
        
    print_colored_message("yellow", "\nOK. You control \n\n\" ----- " + ("Left" if paddle_side == "left" else "Right") + " ----- \"\n")

    print_colored_message("white", "Connecting to: ")
    print_colored_message("yellow", url + "\n")

    # WebSocketの設定と接続
    websocket.enableTrace(False)  # デバッグ情報を出力
    controller = PaddleControl(paddle_side)
    ws_app = create_ws_app(url, controller)
    
    # WebSocketのイベントループを開始
    ws_app.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == "__main__":
    main()