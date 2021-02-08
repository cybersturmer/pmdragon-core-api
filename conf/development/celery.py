#!/usr/bin/env python
from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.development.settings')

app = Celery('pmdragon')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
