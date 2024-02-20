#!/usr/bin/env bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
python manage.py makemigrations users
python manage.py makemigrations market
python manage.py makemigrations data
python manage.py makemigrations notification
python manage.py migrate
#rm -rf /opt/project/storage/