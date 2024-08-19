from django.urls import path

from higher_staff_dashboard.consumers import BusinessGraphConsumerForHigherStaff

websocket_urlpatterns = [
    path('ws/higher-staff-dashboard/<str:business_id>/', BusinessGraphConsumerForHigherStaff.as_asgi()),
]
