#!/bin/sh

cd /usr/src/app/backend

python manage.py makemigrations --noinput
python manage.py migrate --noinput
# todo: 入れる(staticディレクトリを作る)
# python manage.py collectstatic --noinput

# 環境変数のENVIRONMENTの値がdevelopmentの時はrunserverを、productionの時はgunicornを実行
if [ $ENVIRONMENT = "development" ]
then
    python manage.py runserver 0.0.0.0:8002
else
    gunicorn -b 0.0.0.0 -p 8002 core.wsgi:application
fi
