from django.urls import path

from owner_dashboard.consumers import BusinessGraphConsumer

websocket_urlpatterns = [
    path('ws/owner-dashboard/<str:business_id>/', BusinessGraphConsumer.as_asgi()),
]
