#!/usr/bin/env python
from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# @todo Refactor
DEPLOYMENT_TREE = {
    settings.DEPLOYMENT == 'HEROKU': 'conf.production.deployment.heroku',
    settings.DEPLOYMENT == 'DOCKER_COMPOSE': 'conf.production.deployment.docker_compose',
}

os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEPLOYMENT_TREE[True])

app = Celery('pmdragon',
             include=['apps.core.api.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
