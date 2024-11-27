#!/bin/sh

cd backend
python manage.py migrate --no-input
python manage.py collectstatic --no-input
python manage.py runserver --bind 0.0.0.0:8000