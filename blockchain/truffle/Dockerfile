# ベースイメージとして Node.js を使用
FROM node:18

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# package.json と package-lock.json をコピー（存在する場合）
COPY package*.json ./

# 必要なパッケージをインストール
RUN npm install

# Truffle をグローバルにインストール
RUN npm install -g truffle

# プロジェクトのファイルをコンテナにコピー
COPY . .

# コントラクトアドレス保存用のディレクトリを作成
RUN mkdir -p /app/addresses
