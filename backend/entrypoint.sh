#!/bin/sh

python manage.py migrate
python manage.py collectstatic --no-input
gunicorn --bind 0:8000 foodgram.wsgi:application

exec "$@"