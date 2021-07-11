from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from .consumers import \
    IssueMessagesObserver, \
    WorkspaceIssuesObserver, \
    WorkspaceIssueTypeCategoriesObserver, \
    WorkspaceIssueTypeCategoriesIconsObserver, \
    WorkspaceIssueStateCategoriesObserver, \
    WorkspaceIssueEstimationCategoriesObserver


class MultiplexerAsyncJson(AsyncJsonWebsocketDemultiplexer):
    """
    {"stream":"issue_chat","payload":{"text":"Hello world"}}
    """
    applications = {
        'issue_chat': IssueMessagesObserver.as_asgi(),
        'workspace_issues': WorkspaceIssuesObserver.as_asgi(),
        'workspace_issue_types': WorkspaceIssueTypeCategoriesObserver.as_asgi(),
        'workspace_issue_type_icons': WorkspaceIssueTypeCategoriesIconsObserver.as_asgi(),
        'workspace_issue_states': WorkspaceIssueStateCategoriesObserver.as_asgi(),
        'workspace_issue_estimations': WorkspaceIssueEstimationCategoriesObserver.as_asgi(),
    }
