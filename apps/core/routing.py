from django.urls import path

from apps.core.consumers import LiveConsumer, IssueConsumerObserver

websocket_urlpatterns = [
    path('ws/notifications/', LiveConsumer.as_asgi()),
    path('ws/issues/', IssueConsumerObserver.as_asgi())
]
