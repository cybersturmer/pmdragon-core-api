from conf.common.settings import *

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

EMAIL_FROM_BY_DEFAULT = os.getenv('EMAIL_USER')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

EMAIL_USE_SSL = True
EMAIL_PORT = 465

EMAIL_SUBJECT_PREFIX = '[PmDragon] '
