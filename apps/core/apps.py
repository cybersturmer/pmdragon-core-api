from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CoreConfig(AppConfig):
	name = 'apps.core'
	label = 'core'
	verbose_name = _('Core')
	default_auto_field = 'django.db.models.BigAutoField'

	def ready(self):
		# Strange way to import signals and activate them.
		from apps.core import signals
