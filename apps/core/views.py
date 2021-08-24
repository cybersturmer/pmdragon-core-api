from django.views.generic import TemplateView
import urllib.request, json


class MainView(TemplateView):
    template_name = 'index/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with urllib.request.urlopen('https://master.dl.sourceforge.net/project/pmdragon/releases.json?viasf=1') as url:
            # @todo Not the best option - better do it on client.
            data = json.loads(url.read().decode())

            context['version'] = data["version"]
            context['releases'] = json.dumps(data["releases"])
            context['timestamp'] = data['timestamp']

            return context
