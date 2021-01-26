from django.urls import path

from apps.core.consumers import LiveConsumer, IssueConsumerObserver

websocket_urlpatterns = [
    path('notifications/', LiveConsumer.as_asgi()),
    path('issues/', IssueConsumerObserver.as_asgi())
]
