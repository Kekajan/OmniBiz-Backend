from django.urls import re_path
from notification import consumers

websocket_urlpatterns = [
    re_path(r'^ws/notification/(?P<business_id>\w+)/$', consumers.NotificationConsumer.as_asgi()),
]
