from django.views.generic import TemplateView
from django.conf import settings


class SwaggerView(TemplateView):
    template_name = 'core/swagger.html'

    def get_context_data(self, **kwargs):
        """
        If we use swagger in Docker compose - we can use special url from Django url.
        """
        context = super().get_context_data(**kwargs)
        context['heroku'] = (settings.DEPLOYMENT == 'HEROKU')
        return context

