from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from .consumers import IssueMessagesObserver, WorkspaceIssuesObserver


class MultiplexerAsyncJson(AsyncJsonWebsocketDemultiplexer):
    """
    {"stream":"ping","payload":{"text":"Hello world"}}
    """
    applications = {
        'issue_chat': IssueMessagesObserver.as_asgi(),
        'workspace_issues': WorkspaceIssuesObserver.as_asgi()
    }
