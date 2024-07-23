from django.urls import path, re_path

from billing import consumers

websocket_urlpatterns = [
    re_path(r'ws/invoices/(?P<business_id>\w+)/$', consumers.InvoiceConsumer.as_asgi()),
]
