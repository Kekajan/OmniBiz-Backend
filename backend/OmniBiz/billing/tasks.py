from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery import shared_task


@shared_task
def notify_invoice_creation(invoice_id, status, amount):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'invoice_notifications',
        {
            'type': 'invoice_notification',
            'data': {
                'invoice_id': invoice_id,
                'status': status,
                'amount': amount,
            }
        }
    )
