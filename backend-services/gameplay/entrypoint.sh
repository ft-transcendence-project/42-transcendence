#!/bin/sh

if [ $ENVIRONMENT = "development" ]
then
    cd /usr/src/app/gameplay/
else
    cd /usr/src/app/
fi

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py flush --noinput

# 環境変数のENVIRONMENTの値がdevelopmentの時はrunserverを、productionの時はdaphneを実行
if [ $ENVIRONMENT = "development" ]
then
    python manage.py runserver 0.0.0.0:8001
else
    daphne -b 0.0.0.0 -p 8001 core.asgi:application
fi
