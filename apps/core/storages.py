from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# Inspired by https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html
class StaticStorage(S3Boto3Storage):
	location = settings.AWS_STATIC_LOCATION


class PublicMediaStorage(S3Boto3Storage):
	location = settings.AWS_PUBLIC_MEDIA_LOCATION
	file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
	location = settings.AWS_PRIVATE_MEDIA_LOCATION
	default_acl = 'private'
	file_overwrite = False
	custom_domain = False
