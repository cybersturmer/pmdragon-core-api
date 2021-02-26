from conf.common.settings import *

DEBUG = bool(os.getenv('FORCE_DEBUG', False))

ALLOWED_HOSTS = [os.getenv('API_HOSTNAME')]

if api_ip := os.getenv('API_IP'):
    ALLOWED_HOSTS.append(
        api_ip
    )

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
    },
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
})

ROOT_URLCONF = 'conf.production.urls'

"""
Celery settings """
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_BROKER_URL = os.getenv('CLOUDAMQP_URL')
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_CONNECTION_TIMEOUT = 10

"""
Custom EMAIL Settings 
FRONTEND_HOSTNAME just for email replacing """
FRONTEND_HOSTNAME = os.getenv('FRONTEND_HOSTNAME')
EMAIL_FROM_BY_DEFAULT = os.getenv('EMAIL_USER')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

EMAIL_USE_SSL = True
EMAIL_PORT = 465

EMAIL_SUBJECT_PREFIX = '[PmDragon] '

if not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn="https://01423d4007f24bc1bade0cc4ccbb7aa3@o514097.ingest.sentry.io/5616873",
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

HEROKU = bool(os.getenv('HEROKU'))
# Activate Heroku settings for Django.
if HEROKU:
    import django_heroku

    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    MIDDLEWARE.insert(
        1,
        'whitenoise.middleware.WhiteNoiseMiddleware'
    )
    django_heroku.settings(locals(), logging=False)
