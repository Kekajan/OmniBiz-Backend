from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            raise DenyConnection("Unauthenticated user")

        self.room_group_name = f'user_{self.user.user_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        if hasattr(self.user, 'business'):
            self.business_group_name = f'business_{self.user.business_id}'
            await self.channel_layer.group_add(
                self.business_group_name,
                self.channel_name
            )

        await self.channel_layer.group_add(
            'all_users',
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if hasattr(self.user, 'business'):
            await self.channel_layer.group_discard(
                self.business_group_name,
                self.channel_name
            )

        await self.channel_layer.group_discard(
            'all_users',
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if not self.user.is_authenticated:
            return  # Ignore messages from unauthenticated users

        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification_message',
                'message': message
            }
        )

    async def notification_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
