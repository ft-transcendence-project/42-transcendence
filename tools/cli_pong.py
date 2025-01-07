import sys
import tty
import termios
import threading
import time
import select

class PaddleControl:
    def __init__(self):
        self.key_states = {'left': False, 'right': False}
        self.running = True
        self.threads = []  # アクティブなスレッドを追跡
        
    def get_key(self):
        # ターミナルの設定を変更して1文字ずつ読み取り
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            if select.select([sys.stdin], [], [], 0.1)[0]:
                return sys.stdin.read(1)
            return ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def handle_input(self):
        while self.running:
            key = self.get_key().lower()

            if key == '':
                print("No key pressed")

            # 終了条件
            if key == 'q':
                self.running = False
                self.key_states['left'] = False
                self.key_states['right'] = False
                break
                
            # 左パドル制御 (d/e)
            if key in ['d', 'e']:
                if not self.key_states['left']:
                    self.key_states['left'] = True
                    thread = threading.Thread(target=self.continuous_send, args=('left',))
                    self.threads.append(thread)
                    thread.start()
                    
            # 右パドル制御 (i/k)
            elif key in ['i', 'k']:
                if not self.key_states['right']:
                    self.key_states['right'] = True
                    thread = threading.Thread(target=self.continuous_send, args=('right',))
                    self.threads.append(thread)
                    thread.start()
            
            else:
                self.key_states['left'] = False
                self.key_states['right'] = False

    def continuous_send(self, paddle):
        while self.key_states[paddle]:
            print(f"Paddle {paddle} moving...")
            time.sleep(0.1)  # メッセージ送信間隔

    def start(self):
        print("Controls: D/E - Left paddle, I/K - Right paddle, Q - Quit")
        try:
            self.handle_input()
        except KeyboardInterrupt:
            self.running = False
            self.key_states['left'] = False
            self.key_states['right'] = False
        finally:
            # 全スレッドの終了を待機
            for thread in self.threads:
                thread.join(timeout=1.0)

if __name__ == "__main__":
    controller = PaddleControl()
    controller.start()