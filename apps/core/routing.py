from django.urls import path

from apps.core.consumers import IssueConsumerObserver, SprintConsumerObserver, IssueMessagesObserver

websocket_urlpatterns = [
    path('ws/issues/', IssueConsumerObserver.as_asgi()),
    path('ws/sprints/', SprintConsumerObserver.as_asgi()),
    path('ws/messages/', IssueMessagesObserver.as_asgi())
]
