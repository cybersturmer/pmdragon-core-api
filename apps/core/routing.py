from django.urls import path

from apps.core.consumers import IssueMessagesObserver

# For all routes we really need to get token ?token=some_token
websocket_urlpatterns = [
    path('ws/messages/', IssueMessagesObserver.as_asgi())
]
