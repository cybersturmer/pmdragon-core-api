from conf.production.settings import *
import django_heroku
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEPLOYMENT = 'HEROKU'
ALLOWED_HOSTS = [os.getenv('API_HOSTNAME')]

if DATABASE_URL := os.getenv('DATABASE_URL', None):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }

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

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE.insert(
    1,
    'whitenoise.middleware.WhiteNoiseMiddleware'
)

FRONTEND_HOSTNAME = os.getenv('FRONTEND_HOSTNAME')

sentry_sdk.init(
    dsn="https://01423d4007f24bc1bade0cc4ccbb7aa3@o514097.ingest.sentry.io/5616873",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

django_heroku.settings(locals(), logging=False)

