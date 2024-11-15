#!/bin/sh
set -e
python manage.py collectstatic 
python manage.py makemigrations
python manage.py migrate
uwsgi --socket :8000 -master --enable-threads -module server.wsgi