from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
from django.utils import timezone

from Utils.Common.business_data_handling import aggregate_business_data
from cash_book.models import CashBook
from business.models import Business  # Import your Business model

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CashBook)
def notify_graph_update(sender, instance, **kwargs):
    # Extract the business_id from the database name
    # Assuming the database name is in the format: '<business_id>_secondary'
    db_name = instance._state.db
    business_id = db_name.split('_')[0]

    # Fetch the business using business_id from the primary database
    business = Business.objects.using('default').get(business_id=business_id)

    # Get the owner_id from the business
    owner_id = business.owner_id
    logger.info(f"Owner ID: {owner_id}, Timezone-aware: {timezone.is_aware(instance.created_at)}")

    # Aggregate the business data for the owner
    graph_data = aggregate_business_data(owner_id)

    # Send the updated graph data via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'owner_{owner_id}',
        {
            'type': 'graph_update',
            'graph_data': graph_data,
        }
    )
