from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.permissions import AllowAny

from .api.serializers import IssueSerializer, SprintWritableSerializer
from .models import Issue, Sprint, IssueMessage


class IssueMessagesObserver(AsyncAPIConsumer):
    permission_classes = (
        AllowAny,
    )

    @model_observer(IssueMessage)
    async def message_change_handler(self, message, observer=None, action=None, **kwargs):
        await self.send_json(dict(body=message, action=action))

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

    @action()
    async def subscribe_to_messages_in_issue(self, issue_pk, **kwargs):
        issue = await database_sync_to_async(Issue.objects.get, thread_sensitive=True)(pk=issue_pk)
        await self.message_change_handler.subscribe(issue=issue)

    @action()
    async def subscribe_to_message(self, message_pk, **kwargs):
        await self.message_change_handler.subscribe(message=message_pk)


class IssueConsumerObserver(AsyncAPIConsumer):
    async def accept(self, **kwargs):
        await super().accept(** kwargs)
        await self.model_change.subscribe()

    @model_observer(Issue)
    async def model_change(self, message, action=None, **kwargs):
        await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance: Issue, action, **kwargs):
        return IssueSerializer(instance).data


class SprintConsumerObserver(AsyncAPIConsumer):
    async def accept(self, **kwargs):
        await super().accept(** kwargs)
        await self.model_change.subscribe()

    @model_observer(Sprint)
    async def model_change(self, message, action=None, **kwargs):
        await self.send_json(message)

    @model_change.serializer
    def model_serializer(self, instance: Sprint, action, **kwargs):
        return SprintWritableSerializer(instance).data
