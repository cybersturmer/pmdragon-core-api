import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import apps.core.routing as api_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.development.settings')
django.setup()

"""
We recognize protocol and use suited routing for that
For socket we use accumulate all routes for sockets. """
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(api_routing.websocket_urlpatterns)
    ),
})
