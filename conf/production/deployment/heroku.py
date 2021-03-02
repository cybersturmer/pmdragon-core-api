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

CELERY_BROKER_URL = os.getenv('CLOUDAMQP_URL')

"""
S3 settings """
INSTALLED_APPS.append('storages')

# I use BUCKETEER Addon in HEROKU, please change it to your s3.
# Your Amazon Web Services access key, as a string.
AWS_ACCESS_KEY_ID = os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID')

# Your Amazon Web Services secret access key, as a string.
AWS_SECRET_ACCESS_KEY = os.getenv('BUCKETEER_AWS_SECRET_ACCESS_KEY')

AWS_DEFAULT_ACL = 'public-read'

# Your Amazon Web Services storage bucket name, as a string.
AWS_STORAGE_BUCKET_NAME = os.getenv('BUCKETEER_BUCKET_NAME')

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400'
}

# To allow django-admin collectstatic to automatically put your static files in your bucket
AWS_STATIC_LOCATION = 'static'
STATICFILES_STORAGE = 'apps.core.storages.StaticStorage'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'

# To upload media files to S3 set
AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'apps.core.storages.PublicMediaStorage'

AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = 'apps.core.storages.PrivateMediaStorage'


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

FRONTEND_HOSTNAME = os.getenv('FRONTEND_HOSTNAME')

"""
REDIS FOR WEBSOCKETS """
REDIS_CONNECTION = os.getenv('REDIS_URL', None)

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

sentry_sdk.init(
    dsn="https://01423d4007f24bc1bade0cc4ccbb7aa3@o514097.ingest.sentry.io/5616873",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

django_heroku.settings(locals(), logging=False)

