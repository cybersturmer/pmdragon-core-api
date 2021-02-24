#!/usr/bin/env bash

# Please DON'T use it for you project
# This entrypoint is just for debug
# It drops all changes after restarting in Docker
# It also requires data.json in root of project
# Django (python manage.py dumpdata --all > data.json)

echo -e "\e[94m Collecting static...\e[0m"
python manage.py collectstatic --noinput --clear

# Copying api schema to staticfiles (We use it to share on Heroku)
# We don't need it in production.
cp -R templates/api staticfiles/api

echo -e "\e[94m Making migrations...\e[0m"
python manage.py makemigrations
python manage.py migrate

# For this to work you have to add your own data dump
echo -e "\e[94m Loading predefined data...\e[0m"
python manage.py loaddata data.json

echo -e "\e[92m Starting service...\e[0m"
uvicorn conf.asgi:application --uds /uvicorn_socket/uvicorn.socket