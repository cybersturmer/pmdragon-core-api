from conf.production.settings import *

DEPLOYMENT = 'LOCALHOST'
DEBUG = bool(os.getenv('FORCE_DEBUG', False))

ALLOWED_HOSTS.append(
    os.getenv('API_IP')
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': '5432',
    },
}

REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
})

FRONTEND_HOSTNAME = 'https://localhost'
