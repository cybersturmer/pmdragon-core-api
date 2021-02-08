#!/usr/bin/env python
from __future__ import absolute_import

import os

from celery import Celery

from conf.production import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.production.settings')

app = Celery('pmdragon')

CELERY_TIMEZONE = 'UTC'


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)