from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from Utils.Common.find_peoples import get_all_users, get_user_by_id, get_business_people

channel_layer = get_channel_layer()


def create_notification(notification):
    if notification.target == 'all':
        users = get_all_users()
    elif notification.target == 'user':
        users = [get_user_by_id(notification.target_id)]
    elif notification.target == 'business':
        users = get_business_people(notification.target_id)
    else:
        users = None

    for user in users:
        async_to_sync(channel_layer.group_send)(
            f"user_{user.user_id}",
            {
                'type': 'send_message',
                'message': notification.message,
            }
        )
