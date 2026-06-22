@echo off
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
