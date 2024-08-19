import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

import billing.routing
import higher_staff_dashboard.routing
import notification.routing
import owner_dashboard.routing
from Utils.Milddlewares.AuthMiddleware import JWTAuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OmniBiz.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                notification.routing.websocket_urlpatterns +
                billing.routing.websocket_urlpatterns +
                owner_dashboard.routing.websocket_urlpatterns +
                higher_staff_dashboard.routing.websocket_urlpatterns
            )
        )
    ),
})
