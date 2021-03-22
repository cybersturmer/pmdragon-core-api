from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from .consumers import IssueMessagesObserver


class MultiplexerAsyncJson(AsyncJsonWebsocketDemultiplexer):
    """
    {"stream":"ping","payload":{"text":"Hello world"}}
    """
    applications = {
        'issue_chat': IssueMessagesObserver.as_asgi()
    }
