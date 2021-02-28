from conf.production.settings import *

DEPLOYMENT = 'DOCKER_COMPOSE'
DEBUG = bool(os.getenv('FORCE_DEBUG', False))

ALLOWED_HOSTS = ['localhost', os.getenv('API_IP')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pmdragon',
        'USER': 'pmdragon',
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'postgres',
        'PORT': '5432',
    },
}

CELERY_BROKER_URL = 'amqp://rabbit'

REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
})

FRONTEND_HOSTNAME = 'https://localhost'

"""
REDIS FOR WEBSOCKETS """
REDIS_CONNECTION = (os.getenv('REDIS_HOST'), int(os.getenv('REDIS_PORT')))

CHANNEL_LAYERS = {
    "default": {
        'BACKEND': "channels_redis.core.RedisChannelLayer",
        'CONFIG': {
            'hosts': [REDIS_CONNECTION]
        }
    }
}
