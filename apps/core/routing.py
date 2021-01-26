from django.urls import path

from apps.core.consumers import LiveConsumer

websocket_urlpatterns = [
    path('notifications/', LiveConsumer.as_asgi())
]
