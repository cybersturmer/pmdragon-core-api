import asyncio
import json

from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.permissions import IsAuthenticated

from .models import Issue, IssueMessage, Person
from .api.serializers import PersonSerializer


class PingConsumer(AsyncConsumer):
    async def websocket_connect(self, message):
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, message):
        text_message = message.get('text')
        json_message = json.loads(text_message)

        persons = await database_sync_to_async(self.get_persons)()
        json_persons = PersonSerializer(persons)

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(json_persons.data)
        })

    def get_persons(self):
        return Person.objects.all()

    async def websocket_disconnect(self, message):
        pass


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

    """
    Actually we have to check permissions here but we are not able to do that
    Cuz now we don't have user's data., but we will, i promise.
    """
    @action()
    async def subscribe_to_messages_in_issue(self, issue_pk, **kwargs):
        issue = await database_sync_to_async(Issue.objects.get, thread_sensitive=True)(pk=issue_pk)
        await self.message_change_handler.subscribe(issue=issue)
