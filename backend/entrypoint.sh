#!/bin/sh

cd /usr/src/app/backend

python manage.py makemigrations --noinput
python manage.py migrate --noinput
# todo: 入れる(staticディレクトリを作る)
# python manage.py collectstatic --noinput

python manage.py flush --noinput
python manage.py loaddata fixtures/users.json

# 環境変数のENVIRONMENTの値がdevelopmentの時はrunserverを、productionの時はdaphneを実行
if [ $ENVIRONMENT = "development" ]
then
    python manage.py runserver 0.0.0.0:8000
else
    gunicorn -b 0.0.0.0 -p 8000 core.wsgi:application
fi
