from django.urls import path

from apps.core.consumers import IssueMessagesObserver

websocket_urlpatterns = [
    path('ws/messages/', IssueMessagesObserver.as_asgi())
]
