import sys
from datetime import timedelta

from conf.common.settings import *
import django_heroku

DEBUG = True

ALLOWED_HOSTS = ['*']
SECRET_KEY = 'w*ea%hd29u-&l&rol@5zo8a+@5o=@wb+i*r(@_+fnuc!*^9o0w'

"""
JWT Tokens settings """
REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )})

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

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    "SIGNING_KEY": SECRET_KEY,
    'ISSUER': 'PMDragon API',
}

CELERY_BROKER_URL = 'amqp://rabbit'

"""
Django rest framework cors headers """
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'conf.development.urls'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = "/media/"

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

FRONTEND_ICON_SET = 'mdi-'
ICON_CHOICES = (
    (FRONTEND_ICON_SET + 'microsoft-excel', 'Microsoft Excel'),
    (FRONTEND_ICON_SET + 'microsoft-word', 'Microsoft Word'),
    (FRONTEND_ICON_SET + 'microsoft-powerpoint', 'Microsoft Powerpoint'),
    (FRONTEND_ICON_SET + 'file-pdf', 'Adobe PDF'),
    (FRONTEND_ICON_SET + 'file-video', 'Video file'),
    (FRONTEND_ICON_SET + 'file-document', 'Text file'),
    (FRONTEND_ICON_SET + 'zip-box', 'Archive'),
    (FRONTEND_ICON_SET + 'language-python', 'Python'),
    (FRONTEND_ICON_SET + 'language-javascript', 'JavaScript'),
    (FRONTEND_ICON_SET + 'language-html5', 'HTML5'),
    (FRONTEND_ICON_SET + 'language-typescript', 'TypeScript'),
    (FRONTEND_ICON_SET + 'language-cpp', 'C++'),
    (FRONTEND_ICON_SET + 'language-c', 'C'),
    (FRONTEND_ICON_SET + 'language-csharp', 'C#'),
    (FRONTEND_ICON_SET + 'language-go', 'Go'),
    (FRONTEND_ICON_SET + 'language-kotlin', 'Kotlin'),
    (FRONTEND_ICON_SET + 'language-lua', 'Lua'),
    (FRONTEND_ICON_SET + 'language-fortran', 'Fortran'),
    (FRONTEND_ICON_SET + 'language-haskell', 'Haskell'),
    (FRONTEND_ICON_SET + 'language-markdown', 'Markdown'),
    (FRONTEND_ICON_SET + 'language-php', 'PHP'),
    (FRONTEND_ICON_SET + 'language-r', 'R'),
    (FRONTEND_ICON_SET + 'language-ruby', 'Ruby'),
    (FRONTEND_ICON_SET + 'language-rust', 'Rust'),
    (FRONTEND_ICON_SET + 'language-swift', 'Swift'),
    (FRONTEND_ICON_SET + 'language-xaml', 'Xaml'),
    (FRONTEND_ICON_SET + 'language-java', 'Java'),
    (FRONTEND_ICON_SET + 'file-image', 'Image'),
)

# list: mimes list: Extensions, tuple: (language-short, readable), bool: can be previewed
# @todo Refactor mime-type List
FILE_EXTENSIONS_MAPPING = (
    (('application/pdf',), ['xls', 'xlsm', 'xlsx'], ICON_CHOICES[0], False),
    (('application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
     ['doc', 'docx'], ICON_CHOICES[1], False),
    (('application/vnd.ms-pps',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation'),
     ['pps', 'ppt', 'pptx'], ICON_CHOICES[2], False),
    (('application/pdf',), ['pdf'], ICON_CHOICES[3], False),
    (('video/x-msvideo',
      'video/x-flv',
      'video/m4v',
      'video/x-matroska',
      'video/quicktime',
      'video/mp4',
      'video/mpeg',
      'video/mpeg',
      'application/vnd.adobe.flash.movie',
      'video/x-ms-wmv'),
     ['avi', 'flv',
      'm4v', 'mkv', 'mov', 'mp4', 'mpg',
      'mpeg', 'swf', 'wmv'], ICON_CHOICES[4], False),
    (('text/plain',
      'application/rtf',
      'application/vnd.oasis.opendocu'),
     ['txt', 'rtf', 'odt'], ICON_CHOICES[5], False),
    (('application/x-tar',
      'application/zip',
      'application/x-bzip2',
      'application/x-7z-compressed'), ['tar', 'zip', 'bz2', '7z'], ICON_CHOICES[6], False),
    (('text/plain',), ['py'], ICON_CHOICES[7], False),
    (('text/javascript',
      'application/javascript'),
     ['js', 'vue'], ICON_CHOICES[8], False),
    (('text/html',), ['html'], ICON_CHOICES[9], False),
    (('application/javascript',), ['ts'], ICON_CHOICES[10], False),
    (('text/x-c', 'text/plain'), ['cpp', 'h'], ICON_CHOICES[11], False),
    (('text/plain',), ['cs'], ICON_CHOICES[13], False),
    (('text/plain',), ['go'], ICON_CHOICES[14], False),
    (('text/plain', 'text/plain', 'text/plain'),
     ['kt', 'kts', 'ktm'], ICON_CHOICES[15], False),
    (('text/plain',), ['lua'], ICON_CHOICES[16], False),
    (('text/x-fortran',
      'text/x-fortran'), ['f95', 'f03'], ICON_CHOICES[17], False),
    (('text/plain',
      'text/plain'), ['hs', 'hls'], ICON_CHOICES[18], False),
    (('text/markdown',
      'text/markdown'), ['markdown', 'md'], ICON_CHOICES[19], False),
    (('text/html',), ['php'], ICON_CHOICES[20], False),
    (('text/plain',), ['r', 'rdata', 'rds', 'rda'], ICON_CHOICES[21], False),
    (('text/plain',), ['rb'], ICON_CHOICES[22], False),
    (('text/plain',
      'text/plain'), ['rs', 'rlib'], ICON_CHOICES[23], False),
    (('text/plain',), ['swift'], ICON_CHOICES[24], False),
    (('text/plain',), ['xaml'], ICON_CHOICES[25], False),
    (('text/plain',
      'application/java-archive'), ['java', 'jar'], ICON_CHOICES[26], False),
    (('image/bmp',
      'image/gif',
      'image/jpeg',
      'image/jpeg',
      'image/png',
      'image/svg+xml'),
     ['bmp', 'gif', 'jpg', 'jpeg', 'png', 'svg'], ICON_CHOICES[27], True)
)

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
django_heroku.settings(locals(), logging=False)
