#!/usr/bin/env bash
# We use this script for launch it from docker-compose or docker container.
su -m rabbituu -c "celery -A conf.production.celery worker --loglevel=INFO"