from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.permissions import IsAuthenticated

from .models import Issue, IssueMessage, Person
from .api.serializers import PersonSerializer, IssueMessageSerializer
from rest_framework.renderers import JSONRenderer


class IssueMessagesObserver(AsyncAPIConsumer):
    """
    Payload example
    {
      "action": "subscribe_to_messages_in_issue",
      "request_id": 4,
      "issue_pk": 48
    }
    """
    permission_classes = (
        IsAuthenticated,
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
