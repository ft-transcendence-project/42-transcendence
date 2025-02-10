#!/bin/bash

# ホストのIPを取得
# ipコマンドが存在するかどうか
get_host_ip() {
    if command -v ip > /dev/null; then
        # linux
        HOST_IP=$(ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | head -n 1)
    else
        # mac
        HOST_IP=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{ print $2 }')
    fi

    # HOST_IPが存在しない場合にエラーメッセージを表示し終了
    if [ -z "$HOST_IP" ]; then
        echo "Failed to get host IP address"
        exit 1
    fi

    # .envファイルにHOST_IPを追加または上書きする
    if grep -q "^HOST_IP=" .env; then
        # 既存のHOST_IP行を置換
        sed -i '' "s/^HOST_IP=.*/HOST_IP=$HOST_IP/" .env
    else
        # 新しいHOST_IP行を追加
        echo "HOST_IP=$HOST_IP" >> .env
    fi
}

up() {
    get_host_ip
    docker stop $(docker ps -aq)
    docker rm $(docker ps -aq)
    docker rmi $(docker images -q)
    docker volume rm $(docker volume ls -q)
    docker compose -f compose.yaml up --build
}

prod_up() {
    get_host_ip
    docker stop $(docker ps -aq)
    docker rm $(docker ps -aq)
    docker rmi $(docker images -q)
    docker volume rm $(docker volume ls -q)
    docker compose -f compose.yaml -f compose.prod.yaml up --build
}

while getopts :up OPT
do
case $OPT in
u ) up;;
p ) prod_up;;
esac
done
