# Pong Game CLI 操作プログラム 仕様書

## 概要

PongゲームをCLIから操作するプログラム。ユーザーがWebSocketを介して左または右のパドルを操作します。

---

## 動作環境

- **プログラム言語**: Python 3
- **必要ライブラリ**:
  - `websocket-client`
- **OS**: macOS, Linux, Windows

---

## 使用方法

### 1. Python仮想環境の作成と起動

以下のコマンドでPython仮想環境を作成し起動してください。

```bash
python3 -m venv venv
. ./venv/bin/activate
```

### 2. 依存関係のインストール

以下のコマンドで必要なライブラリをインストールしてください。

```bash
pip install -r requirements.txt
```

### 3. プログラムの実行

以下のコマンドでプログラムを実行してください。

```bash
python3 -m srcs.cli_pong_client
```
