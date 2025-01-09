import sys
import termios
import signal
import asyncio
import websockets
import json
import fcntl
import os
import select
import time
import ssl
# from dotenv import load_dotenv
import logging
import requests

# fdの端末属性を取得.後でdefaultに戻す
fd = sys.stdin.fileno()
default_setting = termios.tcgetattr(fd)
new_setting = termios.tcgetattr(fd)

# new[3]はローカルモードフラグで以下を制御できる
# ICANON(カノニカルモードのフラグ)を外す -> Enterキーを待たなくても次に進む
new_setting[3] &= ~termios.ICANON
# ECHO(入力された文字を表示するか否かのフラグ)を外す -> 代わりにprintで表示する
new_setting[3] &= ~termios.ECHO

def handle_sigint(sig, frame):
    print("Ctrl+C pressed")
    exit(0)

def read_key_nonblocking():
    try:
        key = sys.stdin.read(1)
    except IOError:
        key = None
    return key

async def websocket_communication_loop():
    # cert.pemファイルのパスを指定
    cert_file_path = './cert.pem'
    # ファイルを読み込み、内容を出力
    with open(cert_file_path, 'r') as cert_file:
        cert_content = cert_file.read()
        print(cert_content)
    try:
        # logging.basicConfig(level=logging.DEBUG)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # 証明書のCN(42pong.com)の検証を無効にする
        context.check_hostname = True
        # ssl.CERT_REQUIREDにすると[SSL: CERTIFICATE_VERIFY_FAILED]になる
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(cert_file_path)
        # requestsライブラリを使用してHTTPSリクエストを送信
        # response = requests.get('https://localhost:8443', verify=cert_file_path)
        # print(response.text)
        input_uri = input("Enter WebSocket server URI > ")

        # async withブロックを抜けると、接続が自動的に閉じる。
        async with websockets.connect(input_uri, ssl=context, ping_interval=30, ping_timeout=120) as websocket:
            print("Connected to WebSocket server.")
            print("> ")
             # 端末の設定を変更.ノンブロッキングでキー入力を読む
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            termios.tcsetattr(fd, termios.TCSANOW, new_setting)
            while True:
                try:
                    key = read_key_nonblocking()
                    if key:
                        print(f"Key pressed: {key}")
                        if key == 'e':
                            await websocket.send(json.dumps({"action": "pressed", "key": "E"}))
                        elif key == 'd':
                            await websocket.send(json.dumps({"action": "pressed", "key": "D"}))
                        elif key == 'i':
                            await websocket.send(json.dumps({"action": "pressed", "key": "I"}))
                        elif key == 'k':
                            await websocket.send(json.dumps({"action": "pressed", "key": "K"}))
                    await asyncio.sleep(0.01)
                except Exception as e:
                    print(f"Error sending message: {e}")
                    break
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
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # 端末の設定を元に戻す
        termios.tcsetattr(fd, termios.TCSANOW, default_setting)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    asyncio.run(websocket_communication_loop())
