from django.urls import path, re_path
from billing.consumers import InvoiceConsumer

websocket_urlpatterns = [
    re_path(r'^ws/invoices/(?P<business_id>\w+)/$', InvoiceConsumer.as_asgi()),
]
