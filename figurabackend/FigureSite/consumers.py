# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json

class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'notifications_%s' % self.scope['user'].id
        print('HEADERS')
        
        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    async def notify(self, event):
        await self.send()
    async def notification(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['notification_data']))
        