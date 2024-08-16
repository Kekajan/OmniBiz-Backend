from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.serializers import serialize
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Utils.Common.find_peoples import get_all_users, get_user_by_id, get_business_people
from notification.models import Notification
from notification.serializers import NotificationSerializer

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


class GetAllNotificationView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        user = request.user
        user_id = user.user_id

        if not business_id:
            return Response({'Business id not found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            business_notifications = Notification.objects.filter(target_id=business_id)
            user_notifications = Notification.objects.filter(target_id=user_id)
        except Notification.DoesNotExist:
            business_notifications = None
            user_notifications = None
            return Response({'notification not found'}, status=status.HTTP_400_BAD_REQUEST)

        combined_notifications = list(business_notifications) + list(user_notifications)

        if not combined_notifications:
            return Response({'No notifications found'}, status=status.HTTP_400_BAD_REQUEST)

        combined_notifications.sort(key=lambda notification: notification.created_at, reverse=True)

        serializer = NotificationSerializer(combined_notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarksAsReadView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        notification_id = kwargs.get('notification_id')

        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.updated_at = timezone.now()
            notification.save()
            return Response({'notification was marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'No notifications found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteNotificationView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        notification_id = kwargs.get('notification_id')

        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            return Response({'notification was deleted'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'No notifications found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
