import os

import django

django.setup()

from apps.core.middleware import JWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import apps.core.routing as api_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.production.settings')
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
