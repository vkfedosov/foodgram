#!/bin/sh

python manage.py makemigrations
python manage.py migrate
pyrhon manage.py import_data
python manage.py collectstatic --no-input

exec "$@"