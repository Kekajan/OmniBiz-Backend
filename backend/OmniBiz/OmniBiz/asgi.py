"""
ASGI config for OmniBiz project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

import billing.routing
import notification.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OmniBiz.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            notification.routing.websocket_urlpatterns +
            billing.routing.websocket_urlpatterns
        )
    )
})
