import sys
import termios
import signal
import asyncio
import websockets
import json

#標準入力fd取得
fd = sys.stdin.fileno()

#fdの端末属性を取得
#後でdefaultに元に戻す
default = termios.tcgetattr(fd)
new = termios.tcgetattr(fd)

#new[3]はローカルモードフラグで以下を制御できる
#ICANON(カノニカルモードのフラグ)を外す -> Enterキーを待たなくても次に進む
new[3] &= ~termios.ICANON
#ECHO(入力された文字を表示するか否かのフラグ)を外す -> 代わりにprintで表示する
new[3] &= ~termios.ECHO

def handle_sigint(sig, frame):
    print("Ctrl+C pressed")
    exit(0)

async def websocket_communication_loop():
        try:
            input_uri = input("Enter WebSocket server URI > ")
            if input_uri.lower() == "exit":
                print("bye👋")
                return
            # async withブロックを抜けると、接続が自動的に閉じられる。
            async with websockets.connect(input_uri) as websocket:
                print("Connected to WebSocket server. Press 'E' or 'D'.")
                while True:
                    try:
                        # 書き換えたnewをfdに適応する
                        termios.tcsetattr(fd, termios.TCSANOW, new)
                        key = sys.stdin.read(1)
                        if key == 'e':
                            await websocket.send(json.dumps({"action": "pressed", "key": "E"}))
                        elif key == 'd':
                            await websocket.send(json.dumps({"action": "pressed", "key": "D"}))
                        elif key == 'i':
                            await websocket.send(json.dumps({"action": "pressed", "key": "I"}))
                        elif key == 'k':
                            await websocket.send(json.dumps({"action": "pressed", "key": "K"}))
                        elif key == '\x04':
                            print("Ctrl+D pressed")
                            exit(0)
                        print(f"pushed: {key}")
                    finally:
                        # fdの属性を元に戻す
                        termios.tcsetattr(fd, termios.TCSANOW, default)
        except websockets.InvalidURI:
            print("Error: Invalid WebSocket URI")
        except websockets.InvalidHandshake:
            print("Error: WebSocket handshake failed")
        except ConnectionRefusedError:
            print("Error: Connection refused. Is the server running?")
        except TimeoutError:
            print("Error: Connection timed out")
        except EOFError:
            print("Ctrl+D pressed")
            exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    asyncio.run(websocket_communication_loop())
