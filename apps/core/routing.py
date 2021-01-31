from django.urls import path

from apps.core.consumers import IssueConsumerObserver, SprintConsumerObserver

websocket_urlpatterns = [
    path('ws/issues/', IssueConsumerObserver.as_asgi()),
    path('ws/sprints/', SprintConsumerObserver.as_asgi())
]
