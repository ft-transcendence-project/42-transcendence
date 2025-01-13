import websocket
import json
import ssl
import sys
import os
import tty
import termios
import select
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .utils import Utils

base_url = "wss://localhost:8443/gameplay.ws/ponglogic/"

class PaddleControl:
    def __init__(self):
        self.game_id = None
        self.url = ""
        self.running = True
        self.paddle_side = ""
        self.down_key = ""
        self.up_key = ""
    
    # game_idとpaddle_sideを設定するための関数
    def first_setup(self):
        Utils.print_colored_message("green", "Welcome to Pong Game!!!\n")
        Utils.print_colored_message("green", "Please type game id you want to play. ")
        while (True):
            self.game_id = sys.stdin.readline().strip()
            if self.game_id.isnumeric():
                self.url = base_url + self.game_id + "/"
                break
            else:
                Utils.print_colored_message("red", "Invalid input. Please type a number. ")
        Utils.print_colored_message("yellow", f"\nOK. The Game id is \n\n\" ----- " + self.game_id + " ----- \"\n")
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
    
    def copy_certificate_from_docker(self) -> str:
        try:
            subprocess.run(["docker", "cp", "web:/etc/ssl/certs/cert.pem", "."], check=True,stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            return "./cert.pem"
        # check==Trueで例外発生した場合にCalledProcessErrorをキャッチ
        except subprocess.CalledProcessError as e:
            Utils.print_colored_message("red", f"Docker cp failed: {e}")
            return None
        except Exception as e:
            Utils.print_colored_message("red", f"Other errors that occurred with copy_certificate_from_docker: {e}")
            return None

    def connect_to_server(self, cert_file_path: str):
        # WebSocketの設定と接続
        websocket.enableTrace(False)  # デバッグ情報を出力
        ws_app = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        try:
            # wss接続し、WebSocketのイベントループを開始
            ws_app.run_forever(sslopt={"cert_reqs": ssl.CERT_REQUIRED,"ca_certs": cert_file_path})
        except Exception as e:
            Utils.print_colored_message("red", f"Error: {e}")
            return
        finally:
            if os.path.exists(cert_file_path):
                os.remove(cert_file_path)
    
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

    def get_key(self) -> str:
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

    # JSONデータの送信（3秒待機後に送信）
    def send_delayed_message(self, ws, move_direction, action, side):
        message = {
            "move_direction": move_direction,
            "action": action,
            "side": side
        }
        ws.send(json.dumps(message))

    def main(self):
        self.first_setup()
        Utils.print_colored_message("white", "Connecting to: ")
        Utils.print_colored_message("yellow", self.url + "\n")
        cert_file_path = self.copy_certificate_from_docker()
        if cert_file_path is None:
            Utils.print_colored_message("red", "Error: Certificate copy failed")
            return
        self.connect_to_server(cert_file_path)

if __name__ == "__main__":
    controller = PaddleControl()
    controller.main()
