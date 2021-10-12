import os
import sys

from conf.common.settings import *

DEBUG = True
DEPLOYMENT = 'IDE_DEBUG'

ALLOWED_HOSTS = ['*']

# I commit this key intentionally, just for development purpose
# Feel free to change it.
SECRET_KEY = 'k(j%=d1u#@vm*&$4n$o)sy1)9+%l$z1_t2=q!$%%j7p_so0&ib'

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

"""
JWT Tokens settings
We need Session Authentication to have swagger spec. """
REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
})

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

CORS_ALLOWED_ORIGINS = [
	'http://localhost:8000',
	'https://localhost:8000',
	'http://localhost:8080',
	'https://localhost:8080'
]

CORS_ALLOW_METHODS = [
	'DELETE',
	'GET',
	'OPTIONS',
	'PATCH',
	'POST',
	'PUT'
]
