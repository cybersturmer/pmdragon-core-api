#!/usr/bin/env bash
su -m rabbituu -c "celery -A conf.production.celery worker --loglevel=INFO"