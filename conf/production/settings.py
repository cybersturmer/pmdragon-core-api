from conf.common.settings import *

DEBUG = bool(os.getenv('IS_DEBUG', False))

ALLOWED_HOSTS = [os.getenv('HOSTNAME')]

"""
Throttle settings """
REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
})

ROOT_URLCONF = 'conf.production.urls'

"""
Custom EMAIL Settings 
HOST_BY_DEFAULT just for email replacing """
EMAIL_FROM_BY_DEFAULT = os.getenv('EMAIL_USER')
HOST_BY_DEFAULT = 'localhost'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

EMAIL_USE_SSL = True
EMAIL_PORT = 465

EMAIL_SUBJECT_PREFIX = '[PmDragon] '

if DEBUG:
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


# Activate Heroku settings for Django.
if bool(os.getenv('IS_HEROKU')):
    import django_heroku
    django_heroku.settings(locals(), logging=False)
