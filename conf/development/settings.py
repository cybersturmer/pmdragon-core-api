import sys
from conf.common.settings import *

DEBUG = True
HEROKU = False

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'conf.development.urls'

CELERY_BROKER_URL = 'amqp://rabbit'

"""
Custom EMAIL Settings 
HOST_BY_DEFAULT just for email replacing """
EMAIL_FROM_BY_DEFAULT = os.getenv('EMAIL_USER')
HOST_BY_DEFAULT = 'localhost'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[PmDragon] '

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
