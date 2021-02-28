import os
import sys

from conf.common.settings import *

DEBUG = True
HEROKU = False

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'conf.development.urls'

CELERY_BROKER_URL = 'amqp://localhost'

REDIS_CONNECTION = ('localhost', 6379)

CHANNEL_LAYERS = {
    "default": {
        'BACKEND': "channels_redis.core.RedisChannelLayer",
        'CONFIG': {
            'hosts': [REDIS_CONNECTION]
        }
    }
}

DJANGO_CHANNELS_REST_API = {
    "DEFAULT_PERMISSION_CLASSES": ("djangochannelsrestframework.permissions.IsAuthenticated",)
}

"""
Custom EMAIL Settings 
FRONTEND_HOSTNAME just for email replacing """
EMAIL_FROM_BY_DEFAULT = os.getenv('EMAIL_USER')
FRONTEND_HOSTNAME = 'localhost'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[PmDragon] '

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pmdragon',
        'USER': 'pmdragon',
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        '': {'handlers': ['console'], 'level': 'INFO'},
        'django': {'handlers': ['console'], 'level': 'INFO'}
    }
}
