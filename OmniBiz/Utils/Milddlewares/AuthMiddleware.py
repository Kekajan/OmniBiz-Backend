import re
import logging
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from django.db import close_old_connections
from rest_framework_simplejwt.exceptions import TokenError

from Utils.Database.Database_Routing.add_database import add_database

logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    """Middleware to authenticate user for channels"""

    def __init__(self, app):
        """Initialize the app."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Authenticate the user based on jwt."""
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.tokens import AccessToken

        close_old_connections()
        try:
            query_string = scope["query_string"].decode("utf8")
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]

            if token:
                try:
                    access_token = AccessToken(token)
                    user_id = access_token["user_id"]
                    user = await self.get_user(user_id)
                    if user:
                        scope['user'] = user
                    else:
                        scope['user'] = AnonymousUser()
                except TokenError as e:
                    logger.error(f"Authentication error: {e}")
                    scope['user'] = AnonymousUser()
            else:
                scope['user'] = AnonymousUser()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            scope['user'] = AnonymousUser()
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        from authentication.models import User
        try:
            add_database('omnibiz')
            user = User.objects.using('omnibiz').get(pk=user_id)
            return user
        except User.DoesNotExist:
            logging.info(f"User {user_id} does not exist")
            return None


def JWTAuthMiddlewareStack(app):
    return JWTAuthMiddleware(AuthMiddlewareStack(app))
