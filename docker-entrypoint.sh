#!/usr/bin/env bash

echo -e "\e[94m Collecting static...\e[0m"
python manage.py collectstatic --noinput --clear

# Copying api schema to staticfiles (We use it to share on Heroku)
# We don't need it in production.
cp -R templates/api staticfiles

echo -e "\e[94m Making migrations...\e[0m"
python manage.py makemigrations
python manage.py migrate

echo -e "\e[92m Starting service...\e[0m"
uvicorn conf.asgi:application --uds /uvicorn_socket/uvicorn.socket