#!/bin/sh

if [ $ENVIRONMENT = "development" ]
then
    cd /usr/src/app/tournament/
else
    cd /usr/src/app/
fi

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py flush --noinput

# 環境変数のENVIRONMENTの値がdevelopmentの時はrunserverを、productionの時はgunicornを実行
if [ $ENVIRONMENT = "development" ]
then
    python manage.py runserver 0.0.0.0:8002
else
    gunicorn --bind 0.0.0.0:8002 core.wsgi:application
fi
