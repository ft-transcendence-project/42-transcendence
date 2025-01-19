#!/bin/bash

# ホストのIPを取得
# ipコマンドが存在するかどうか
if command -v ip > /dev/null; then
    # linux
    HOST_IP=$(ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | head -n 1)
else
    # mac
    HOST_IP=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{ print $2 }')
fi
echo "HOST_IP=$HOST_IP" >> .env
docker-compose up
