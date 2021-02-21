from django.urls import path
from apps.core.multiplexer import MultiplexerAsyncJson

websocket_urlpatterns = [
    path('ws/', MultiplexerAsyncJson.as_asgi())
]
