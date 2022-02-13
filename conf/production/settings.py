import os
from datetime import timedelta

from conf.common.settings import *

TESTING = False

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
SIMPLE_JWT = {
	'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
	'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
	'ROTATE_REFRESH_TOKENS': True,
	'BLACKLIST_AFTER_ROTATION': True,
	'ALGORITHM': 'HS256',
	"SIGNING_KEY": SECRET_KEY,
	'ISSUER': 'PmDragon API',
}

ROOT_URLCONF = 'conf.production.urls'

"""
Celery settings """
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_CONNECTION_TIMEOUT = 10

"""
Custom EMAIL Settings
FRONTEND_HOSTNAME just for email replacing """

EMAIL_FROM_BY_DEFAULT = os.getenv('EMAIL_USER')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

EMAIL_USE_SSL = True
EMAIL_PORT = 465

EMAIL_SUBJECT_PREFIX = '[PmDragon] '

CORS_ALLOWED_ORIGINS = []

CORS_ADDITIONAL_HOST = os.getenv('CORS_ADDITIONAL_HOST')

if CORS_ADDITIONAL_HOST:
	CORS_ALLOWED_ORIGINS.append(CORS_ADDITIONAL_HOST)

CORS_ALLOW_METHODS = [
	'DELETE',
	'GET',
	'OPTIONS',
	'PATCH',
	'POST',
	'PUT'
]
