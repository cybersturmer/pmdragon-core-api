import os

from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'channels',
	'apps.core.apps.CoreConfig',
	'django_filters',
	'rest_framework',
	'corsheaders',
	'drf_yasg',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'conf.wsgi.application'
ASGI_APPLICATION = 'conf.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

LANGUAGES = (
	('en', _('English')),
	('ru', _('Russian')),
	('de', _('German'))
)

LANGUAGE_CODE = 'en-us'

LOCALE_PATHS = (
	os.path.join(BASE_DIR, 'conf/translations'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static'),
)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': (
		'rest_framework.permissions.IsAuthenticated',
	),
	'DEFAULT_FILTER_BACKENDS': (
		'django_filters.rest_framework.DjangoFilterBackend',
	),
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	)
}

LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

"""
Bleach allowed """
BLEACH_ALLOWED_TAGS = [
	'a',
	'abbr',
	'acronym',
	'b',
	'blockquote',
	'code',
	'em',
	'i',
	'li',
	'ol',
	'p',
	'span',
	'strong',
	'strike',
	'u',
	'ul'
]

"""
We really need:
 1) data-mentioned-user-id (Mentioned snippet for issue messages)
 2) @todo Block preview attachment in issue message
"""
BLEACH_ALLOWED_ATTRIBUTES = {
	'a': ['href', 'rel'],
	'span': ['title', 'data-mentioned-user-id', 'class', 'contenteditable'],
	'*': []
}

BLEACH_ALLOWED_PROTOCOLS = [
	'http',
	'https',
	'mailto'
]

BLEACH_STRIPPING = True

SWAGGER_SETTINGS = {
	'USE_SESSION_AUTH': False,
	'JSON_EDITOR': True,
	'SECURITY_DEFINITIONS': {
		'Bearer': {
			'type': 'apiKey',
			'name': 'Authorization',
			'in': 'header'
		}
	}
}

PMDRAGON_ISSUE_DO_NOT_WATCH_FIELDS = [
		'workspace',
		'number',
		'created_by',
		'updated_by',
		'created_at',
		'updated_at'
]

PMDRAGON_ISSUE_FOREIGN_DATA = [
		'workspace',
		'project',
		'type_category',
		'state_category',
		'estimation_category',
		'assignee'
]
