import json
import urllib.request

from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'index/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with urllib.request.urlopen('https://phoenixnap.dl.sourceforge.net/project/pmdragon/releases.json') as url:
            # @todo Not the best option - better do it on client.
            data = json.loads(url.read().decode())

            context['version'] = data["version"]
            context['releases'] = json.dumps(data["releases"])
            context['timestamp'] = data['timestamp']

            return context
