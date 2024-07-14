from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render


def create_notification(user, business_id, message, notification_type):
    from notification.models import Notification
    notification = Notification.objects.create(
        user=user,
        business_id=business_id,
        message=message,
        type=notification_type,
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user.id}',  # Ensure it matches the consumer
        {
            'type': 'notification_message',
            'message': message,
        }
    )
