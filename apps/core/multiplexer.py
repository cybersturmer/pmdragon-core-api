from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from .consumers import PingConsumer


class MultiplexerAsyncJson(AsyncJsonWebsocketDemultiplexer):
    """
    {"stream":"ping","payload":{"text":"Hello world"}}
    """
    applications = {
        "ping": PingConsumer.as_asgi()
    }
