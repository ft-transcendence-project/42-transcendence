import websocket
import json
import ssl
import sys
import os
import tty
import termios
import select
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .utils import Utils

base_ws_url = "wss://localhost:8443/gameplay.ws/ponglogic/"
game_setting_url = "https://localhost:8443/42pong.api/gameplay/gamesetting/api/"
login_url = "https://localhost:8443/42pong.api/account/accounts/api/login/"

class PaddleControl:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.login_token = ""
        self.game_id = None
        self.ws_url = ""
        self.running = True
        self.paddle_side = ""
        self.down_key = ""
        self.up_key = ""
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
                self.send_delayed_message(ws, 'down', 'stop', self.paddle_side)

            # 終了条件
            if key == 'q':
                self.running = False
                ws.close()
                break

            if key == self.down_key:
                self.send_delayed_message(ws, 'down', 'start', self.paddle_side)

            if key == self.up_key:
                self.send_delayed_message(ws, 'up', 'start', self.paddle_side)

    def start(self, ws):
        Utils.print_colored_message("green", "Start by typing the space key!")
        while (True):
            user_input = sys.stdin.readline().rstrip('\n')
            if user_input == ' ':
                message = {
                    "game_signal": "start"
                }
                ws.send(json.dumps(message))
                break

        if self.paddle_side == 'left':
            Utils.print_colored_message("white", "Controls: D - down, E - up, Q - Quit")
            self.down_key = 'd'
            self.up_key = 'e'
        elif self.paddle_side == 'right':
            Utils.print_colored_message("white", "Controls: K - down, I - up, Q - Quit")
            self.down_key = 'k'
            self.up_key = 'i'
        try:
            self.handle_input(ws)
        except KeyboardInterrupt:
            self.running = False

    # JSONデータの送信（3秒待機後に送信）
    def send_delayed_message(self, ws, move_direction, action, side):
        message = {
            "move_direction": move_direction,
            "action": action,
            "side": side
        }
        ws.send(json.dumps(message))
    
    # JSONデータの送信
    def on_open(self, ws):
        Utils.print_colored_message("green", "Connecttion Success!\n")
        self.start(ws)
    
    # メッセージ受信時の処理
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get('game_over'):
                Utils.print_colored_message("green", "Game over!\n")
                ws.close()
        except json.JSONDecodeError:
            Utils.print_colored_message("red", "Error for data\n")
    
    # エラー時の処理
    def on_error(self, ws, error):
        Utils.print_colored_message("red", "Error for websocket: " + error + "\n")
    
    # 接続が閉じられたときの処理
    def on_close(self, ws, close_status_code, close_msg):
        Utils.print_colored_message("red", "Disconnected\n")

    def join_game(self):
        Utils.print_colored_message("green", "Please type game id you want to play. ")
        while (True):
            self.game_id = sys.stdin.readline().strip()
            if self.game_id.isnumeric():
                self.ws_url = base_ws_url + self.game_id + "/"
                break
            else:
                Utils.print_colored_message("red", "Invalid input. Please type a number. ")
        Utils.print_colored_message("yellow", f"\nOK. The Game id is \n\n\" ----- " + self.game_id + " ----- \"\n")

    def post_game_setting(self, ball_velocity, ball_size, map):
        game_setting = {
            "ball_velocity": ball_velocity,
            "ball_size": ball_size,
            "map": map
        }
        headers = {
            "Content-Type": "application/json",  # 必須: JSON形式を指定
        }

        try:
            response = requests.post(game_setting_url, json=game_setting, headers=headers, verify=False)

            # レスポンスのステータスコードをチェック
            if response.status_code == 201:
                self.game_id = response.json().get('id')
                self.ws_url = base_ws_url + str(self.game_id) + "/"
                Utils.print_colored_message("yellow", f"Game created successfully. The Game id is \n\n\" ----- " + str(self.game_id) + " ----- \"\n")
            else:
                Utils.print_colored_message("red", f"Failed to create game. Server responded with status code {response.status_code}.")
                sys.exit(1)

        except requests.RequestException as e:
            # リクエストのエラー（接続エラーなど）
            Utils.print_colored_message("red", f"Error occurred while creating game: {str(e)}")
            sys.exit(1)

    def create_game(self):
        Utils.print_colored_message("green", "Let's set up a new game.\n")
        ball_velocity = ""
        ball_size = ""
        map = ""
        Utils.print_colored_message("green", "Select ball velocity.\nType 1(Fast), 2(Normal), or 3(Slow)")
        while (True):
            user_input = sys.stdin.readline().strip()
            if user_input == '1':
                ball_velocity = "fast"
                break
            elif user_input == '2':
                ball_velocity = "normal"
                break
            elif user_input == '3':
                ball_velocity = "slow"
                break
            else:
                Utils.print_colored_message("red", "Invalid input. Please type 1(Fast) or 2(Normal) or 3(Slow).")

        Utils.print_colored_message("green", "Select ball size.\nType 1(Big), 2(Normal), or 3(Small)")
        while (True):
            user_input = sys.stdin.readline().strip()
            if user_input == '1':
                ball_size = "big"
                break
            elif user_input == '2':
                ball_size = "normal"
                break
            elif user_input == '3':
                ball_size = "small"
                break
            else:
                Utils.print_colored_message("red", "Invalid input. Please type 1(Big) or 2(Normal) or 3(Small).")

        Utils.print_colored_message("green", "Select map.\nType 1(A), 2(B), or 3(C)")
        while (True):
            user_input = sys.stdin.readline().strip()
            if user_input == '1':
                map = "a"
                break
            elif user_input == '2':
                map = "b"
                break
            elif user_input == '3':
                map = "c"
                break
            else:
                Utils.print_colored_message("red", "Invalid input. Please type 1(Big) or 2(Normal) or 3(Small).")

        self.post_game_setting(ball_velocity, ball_size, map)
        Utils.print_colored_message("white", "Please access the following URL from the browser.")
        Utils.print_colored_message("yellow", f"https://localhost:8443/#/gameplay.{self.game_id}/\n")

    def first_setup(self):
        Utils.print_colored_message("green", "Welcome to Pong Game!!!\n")
        Utils.print_colored_message("green", "Press 1 to join an existing game, or 2 to create your own!")
        while (True):
            user_input = sys.stdin.readline().strip()
            if user_input == '1':
                self.join_game()
                break
            elif user_input == '2':
                self.create_game()
                break
            else:
                Utils.print_colored_message("red", "Invalid input. Please type 1(Join) or 2(Create).")

        Utils.print_colored_message("green", "Which paddle do you want to control?\nType D(Left) or K(Right)")
        while (True):
            user_input = sys.stdin.readline().strip()
            print(user_input)
            if user_input in ['D', 'd']:
                self.paddle_side = 'left'
                break
            elif user_input in ['K', 'k']:
                self.paddle_side = 'right'
                break
            else:
                Utils.print_colored_message("red", "Invalid input. Please type D(Left) or K(Right).")
        Utils.print_colored_message("yellow", "\nOK. You control \n\n\" ----- " + ("Left" if self.paddle_side == "left" else "Right") + " ----- \"\n")

    def post_login(self):
        headers = {
            "Content-Type": "application/json",
        }

        Utils.print_colored_message("green", "Please type your username.")
        self.username = sys.stdin.readline().strip()

        Utils.print_colored_message("green", "Please type your password.")
        self.password = sys.stdin.readline().strip()

        login_info = {
            "username": self.username,
            "password": self.password
        }

        try:
            response = requests.post(login_url, headers=headers, json=login_info, verify=False)

            if response.status_code == 200:
                Utils.print_colored_message("green", "Logged in successfully!\n")
                self.login_token = response.json().get('token')
            else:
                Utils.print_colored_message("red", "Failed to log in. Please check your username and password.\n")
                self.login()
        except Exception as e:
            Utils.print_colored_message("red", f"An error occurred:{e}\n")
            sys.exit(1)

    def login(self):
        Utils.print_colored_message("green", "Do you want to log in? (Y/N)")
        while (True):
            user_input = sys.stdin.readline().strip()
            if user_input in ['Y', 'y']:
                self.post_login()
                break
            elif user_input in ['N', 'n']:
                break
            else:
                Utils.print_colored_message("red", "Invalid input. Please type Y(Yes) or N(No).")

    def main(self):
        self.login()

        self.first_setup()
    
        Utils.print_colored_message("white", "Connecting to: ")
        Utils.print_colored_message("yellow", self.ws_url + "\n")
    
        # WebSocketの設定と接続
        websocket.enableTrace(False)  # デバッグ情報を出力
        ws_app = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        
        # WebSocketのイベントループを開始
        ws_app.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == "__main__":
    controller = PaddleControl()
    controller.main()