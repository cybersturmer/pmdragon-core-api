from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from .consumers import PingConsumer, IssueMessagesObserver


class MultiplexerAsyncJson(AsyncJsonWebsocketDemultiplexer):
    """
    {"stream":"ping","payload":{"text":"Hello world"}}
    """
    applications = {
        "ping": PingConsumer.as_asgi(),
        'issue_chat': IssueMessagesObserver.as_asgi()
    }
