import json
import logging
import os

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db import close_old_connections, connections

from Utils.Database.Database_Routing.add_database import add_database


class InvoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Ensure old connections are closed
        await sync_to_async(close_old_connections)()

        self.business_id = self.scope['url_route']['kwargs']['business_id']
        self.group_name = f'business_{self.business_id}'
        user = self.scope["user"]

        if not user.is_authenticated:
            raise DenyConnection("Unauthorized access")

        # user_role = user.role
        #
        # if user_role == "admin":
        #     raise DenyConnection("Admin cannot access business")
        #
        # if user_role == "higher-staff":
        #     if not await self.is_higher_staff_allowed(user.user_id):
        #         raise DenyConnection("You cannot access this business")
        #
        # if user_role == "staff":
        #     if not await self.is_staff_allowed(user.user_id):
        #         raise DenyConnection("You cannot access this business")
        #
        # if user_role == "owner":
        #     if not await self.is_owner_allowed(user.user_id):
        #         raise DenyConnection("You cannot access this business")

        # Connect to the business-specific database
        await self.connect_to_business_db()

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Ensure old connections are closed
        sync_to_async(close_old_connections)()

        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        # Close the database connection
        await self.close_business_db()

    async def receive(self, text_data):
        # Ensure old connections are closed
        await sync_to_async(close_old_connections)()

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        user = self.scope["user"]
        if not user.is_authenticated:
            from Utils.Common.is_user_in_business import is_user_in_business
            is_allow = await database_sync_to_async(is_user_in_business)(user, self.business_id)
            logging.info(is_allow)
            if not is_allow:
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
        sync_to_async(close_old_connections)()

        db_name = f"{self.business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)
        connection = connections[db_name]
        connection.ensure_connection()

    @database_sync_to_async
    def close_business_db(self):
        sync_to_async(close_old_connections)()  # Sync operation to ensure no old connections are used

        db_name = f"{self.business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)
        connection = connections[db_name]
        connection.close()

    @database_sync_to_async
    def is_higher_staff_allowed(self, user_id):
        sync_to_async(close_old_connections)()  # Sync operation to ensure no old connections are used

        from authentication.models import HigherStaffAccess
        add_database(os.getenv("DB_NAME_PRIMARY"))
        try:
            business_ids = HigherStaffAccess.objects.using(os.getenv("DB_NAME_PRIMARY")).filter(user_id=user_id)
            return self.business_id in business_ids
        except HigherStaffAccess.DoesNotExist:
            return False

    @database_sync_to_async
    def is_staff_allowed(self, user_id):
        sync_to_async(close_old_connections)()  # Sync operation to ensure no old connections are used

        from authentication.models import User
        add_database(os.getenv("DB_NAME_PRIMARY"))
        try:
            business_id = User.objects.get(user_id=user_id).business_id
            return self.business_id == business_id
        except User.DoesNotExist:
            return False

    @database_sync_to_async
    def is_owner_allowed(self, user_id):
        sync_to_async(close_old_connections)()  # Sync operation to ensure no old connections are used

        from business.models import Business
        try:
            business_id = Business.objects.get(owner_id=user_id).business_id
            return self.business_id == business_id
        except Exception as e:
            logging.error(f"Error fetching owner business ID: {e}")
            return False
