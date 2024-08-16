from django.urls import path

from notification.views import GetAllNotificationView, MarksAsReadView, DeleteNotificationView

urlpatterns = [
    path('list-notifications/<str:business_id>', GetAllNotificationView.as_view(), name='list-notifications'),
    path('mark-notification/<str:notification_id>', MarksAsReadView.as_view(), name='mark-notifications'),
    path('delete-notification/<str:notification_id>', DeleteNotificationView.as_view(), name='delete-notifications'),
]
