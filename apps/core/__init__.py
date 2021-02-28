from django.conf import settings

if settings.DEBUG:
    from conf.development.celery import app as celery_app
else:
    from conf.production.celery import app as celery_app
__all__ = ('celery_app',)
