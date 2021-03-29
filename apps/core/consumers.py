from channels.db import database_sync_to_async
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.permissions import IsAuthenticated

from .api.serializers import \
    IssueMessageSerializer, \
    IssueSerializer

from .models import \
    Issue,\
    IssueMessage,\
    Person,\
    Workspace


class IssueMessagesObserver(AsyncAPIConsumer):
    """
    This consumer allow us to subscribe to all messages in give issue.
    By checking permission we have to check that issue belong to one of
    workspace that person participated in.
    Payload example
    {
      "action": "subscribe_to_messages_in_issue",
      "request_id": 4,
      "issue_pk": 48
    }
    """
    permission_classes = (
        IsAuthenticated,  # Special async permission
    )

    @model_observer(IssueMessage)
    async def message_change_handler(self, message, observer=None, action=None, **kwargs):
        await self.send_json(dict(message=message, action=action))

    @message_change_handler.serializer
    def model_serializer(self, instance: IssueMessage, action, **kwargs):
        return IssueMessageSerializer(instance).data

    @message_change_handler.groups_for_signal
    def message_change_handler(self, instance: IssueMessage, **kwargs):
        yield f'-issue__{instance.issue_id}'
        yield f'-pk__{instance.pk}'

    @message_change_handler.groups_for_consumer
    def message_change_handler(self, issue=None, message=None, **kwargs):
        if issue is not None:
            yield f'-issue__{issue.pk}'
        if message is not None:
            yield f'-pk__{message.pk}'

    @database_sync_to_async
    def get_issue_filter_data(self, issue_pk, **kwargs):
        user = self.scope.get('user')
        person = Person.objects.get(user=user)

        issue = Issue.objects.get(
            id=issue_pk,
            workspace__participants__in=[person])

        return issue

    @action()
    async def subscribe_to_messages_in_issue(self, issue_pk, **kwargs):
        try:
            issue = await self.get_issue_filter_data(issue_pk=issue_pk)
            await self.message_change_handler.subscribe(issue=issue)
        except Issue.DoesNotExist:
            print('Unable to subscribe messages cause issue was not found')

    @action()
    async def unsubscribe_from_messages_in_issue(self, issue_pk, **kwargs):
        try:
            issue = await self.get_issue_filter_data(issue_pk=issue_pk)
            await self.message_change_handler.unsubscribe(issue=issue)
        except Issue.DoesNotExist:
            print('Unable to unsubscribe messages cause issue was not found')


class WorkspaceIssuesObserver(AsyncAPIConsumer):
    """
    This consumer allow us to subscribe to all issues in give workspace.
    By checking permission we have to check that person participate in given workspace.
    Payload example
    {
        "action": "subscribe_to_issues_in_workspace",
        "request_id": 4,
        "workspace_pk": 34
    }
    """
    permission_classes = (
        IsAuthenticated,  # Special async permission
    )

    @model_observer(Issue)
    async def issue_change_handler(self, message, observer=None, action=None, **kwargs):
        await self.send_json(dict(message=message, action=action))

    @issue_change_handler.serializer
    def model_serializer(self, instance: Issue, **kwargs):
        return IssueSerializer(instance).data

    @issue_change_handler.groups_for_signal
    def issue_change_handler(self, instance: Issue, **kwargs):
        yield f'-workspace__{instance.workspace_id}'
        yield f'-pk__{instance.pk}'

    @issue_change_handler.groups_for_consumer
    def issue_change_handler(self, workspace=None, issue=None, **kwargs):
        if workspace is not None:
            yield f'-workspace__{workspace.pk}'
        if issue is not None:
            yield f'-pk__{issue.pk}'

    @database_sync_to_async
    def get_workspace_filter_data(self, workspace_pk, **kwargs):
        user = self.scope.get('user')
        person = Person.objects.get(user=user)

        workspace = Workspace.objects.get(id=workspace_pk,
                                          participants__in=[person])

        return workspace

    async def subscribe_to_issues_in_workspace(self, workspace_pk, **kwargs):
        try:
            workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
            await self.issue_change_handler.subscribe(workspace=workspace)
        except Workspace.DoesNotExist:
            print('Unable to subscribe issues cause workspace was not found')

    async def unsubscribe_from_issues_in_workspace(self, workspace_pk, **kwargs):
        try:
            workspace = await self.get_workspace_filter_data(workspace_pk=workspace_pk)
            await self.issue_change_handler.unsubscribe(workspace=workspace)
        except Workspace.DoesNotExist:
            print('Unable to unsubscribe issues cause workspace was not found')
