import json
import logging
import os

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import close_old_connections, connections

from Utils.Database.Database_Routing.add_database import add_database


class InvoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.business_id = self.scope['url_route']['kwargs']['business_id']
        self.group_name = f'business_{self.business_id}'
        user = self.scope["user"]

        if not user.is_authenticated:
            from Utils.Common.is_user_in_business import is_user_in_business
            is_allow = is_user_in_business(user, self.business_id)
            if not is_allow:
                self.close()
                raise DenyConnection("Unauthenticated user")

        # Connect to the business-specific database
        await self.connect_to_business_db()

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

        # Close the database connection
        await self.close_business_db()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'invoice_message',
                'message': message
            }
        )

    async def invoice_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def connect_to_business_db(self):
        db_name = f"{self.business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)
        connection = connections[db_name]
        connection.ensure_connection()

    @database_sync_to_async
    def close_business_db(self):
        db_name = f"{self.business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)
        connection = connections[db_name]
        connection.close()
