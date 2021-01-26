from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from channels.generic.websocket import WebsocketConsumer
import json
from .api.serializers import IssueSerializer
from .models import Issue

from djangochannelsrestframework.observer import model_observer


class LiveConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': f'I got your message "{message}"'
        }))


class IssueConsumerObserver(AsyncAPIConsumer):
    async def accept(self, **kwargs):
        await super().accept(** kwargs)
        await self.model_change.subscribe()

    @model_observer(Issue)
    async def model_change(self, message, action=None, **kwargs):
        await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        return IssueSerializer(instance).data
