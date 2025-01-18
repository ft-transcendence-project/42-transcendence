# 42-transcendence

## 概要

オンラインでPongゲームが対戦できるWebアプリケーションプラットフォームです。WebSocketによるリアルタイム通信を実装し、遅延の少ない快適な対戦を実現します。また、ブロックチェーン技術を活用して試合結果を改ざん不可能な形で記録します。

## 主な機能

### 🎮 リアルタイムPongゲーム対戦

- カスタマイズ可能なゲーム設定（ボール速度、サイズなど）
- WebSocketを使用したリアルタイム通信
- キーボード操作によるパドル制御
- リアルタイムスコア表示

### 🏆 トーナメントシステム

- 最大8人参加のトーナメント形式対戦
- 試合結果の自動記録
- トーナメント表のリアルタイム更新
- 優勝者の記録と表示

### 👤 アカウント管理

- 42 OAuth認証による安全なログイン
- Google Authenticatorによる2要素認証(OTP)

### 🌐 マルチ言語対応

- 日本語
- 英語
- 中国語
- i18n による言語切り替え

### ⛓ ブロックチェーン連携

- スマートコントラクトによる試合結果の記録
- Ganacheを使用したローカルブロックチェーン環境
- 改ざん防止と透明性の確保

## 技術スタック

### フロントエンド

- JavaScript (Vanilla JS)
  - モジュール化されたコンポーネント設計
  - カスタムルーター実装
  - SPA
- HTML5 Canvas
  - ゲーム描画エンジン
  - アニメーション処理
- WebSocket
  - リアルタイム双方向通信
  - イベント駆動型アーキテクチャ

### バックエンド

- Django / Django REST Framework
  - RESTful API実装
  - ORM によるデータベース操作
- Django Channels
  - WebSocket (ASGI) 対応
  - 非同期処理
- JWT認証
  - セキュアなAPI通信
  - OAuthトークン管理

### インフラ

- Docker / Docker Compose
  - マルチコンテナ環境
  - 開発/本番環境の一元管理
- Nginx
  - リバースプロキシ
  - SSL/TLS対応
  - WebSocket プロキシ
- PostgreSQL
  - ユーザー情報管理
  - ゲーム記録保存
- Redis
  - セッション管理
  - キャッシュ
- ELK Stack
  - 分散ログ収集
  - リアルタイムログ分析
- Ganache
  - ローカルブロックチェーン環境
  - スマートコントラクトテスト

## セットアップ

### 前提条件

- Docker
- Docker Compose
- Node.js >= 14
- Python >= 3.9

### インストール手順

1. リポジトリのクローン:

```sh
git clone [repository-url]
cd 42-transcendence
```

2. 環境変数の設定:

```sh
cp .env_template .env
# .envファイルを編集して必要な値を設定
```

3. Dockerコンテナの起動:

- 開発環境

```sh
docker compose up --watch --build
```

- 本番環境

```sh
docker compose -f compose.yaml -f compose.prod.yaml up --build
```

4. サイトへのアクセス

- 開発環境
  http://localhost:3000/

- 本番環境
  https://localhost:8443/

## 開発者向け情報

### APIドキュメント

- REST API (OpenAPI):

openapi

- アカウント管理API
- トーナメントAPI
- OAuth認証API
- ゲーム設定API

- WebSocket API (AsyncAPI):

asyncapi

- ゲームロジックAPI
- リアルタイム通信仕様

### CLIツール

- CLIクライアント:

cli_pong_client

- API統合によるCLIでのアプリケーション
- WebSocket接続でプレイ可能
- ログイン機能あり

### ログ管理

- Kibanaダッシュボード:

https://localhost:5601

- アプリケーションログ
- アクセスログ
- エラーログ

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。

## 貢献者

四二高校東京分校卓球愛好会の部員一同
