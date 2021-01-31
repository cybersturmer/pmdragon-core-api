from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from channels.generic.websocket import WebsocketConsumer
import json
from .api.serializers import IssueSerializer, SprintWritableSerializer
from .models import Issue, Sprint

from djangochannelsrestframework.observer import model_observer


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
