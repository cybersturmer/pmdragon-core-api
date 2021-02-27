import os

import django
from django.conf import settings

django.setup()

from apps.core.middleware import JWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import apps.core.routing as api_routing

# @todo Refactor
DEPLOYMENT_TREE = {
    settings.DEPLOYMENT == 'HEROKU': 'conf.production.deployment.heroku',
    settings.DEPLOYMENT == 'DOCKER_COMPOSE': 'conf.production.deployment.docker_compose',
}

os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEPLOYMENT_TREE[True])
http_asgi_application = get_asgi_application()

"""
We recognize protocol and use suited routing for that
For socket we use accumulate all routes for sockets. """
application = ProtocolTypeRouter({
    'http': http_asgi_application,
    'websocket': JWTAuthMiddleware(
        URLRouter(
            api_routing.websocket_urlpatterns,
        )
    )
})
