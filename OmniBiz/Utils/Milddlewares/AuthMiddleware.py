import re
import logging
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.db import close_old_connections
from rest_framework_simplejwt.exceptions import TokenError

from Utils.Database.Database_Routing.add_database import add_database

logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    """Middleware to authenticate and authorize user for channels"""

    def __init__(self, app):
        """Initialize the app."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Authenticate the user based on jwt."""
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.tokens import AccessToken

        await sync_to_async(close_old_connections)()

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
                        role = user.role
                        path = scope["path"]
                        paths = path.split("/")
                        business_id = paths[len(paths) - 2]
                        if await self.is_authorized(user, role, business_id):
                            scope['user'] = user
                        else:
                            logger.error(f"User {user_id} is not authorized for business {business_id}")
                            scope['user'] = AnonymousUser()
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

    @database_sync_to_async
    def is_authorized(self, user, role, business_id):
        from business.models import Business
        from authentication.models import HigherStaffAccess

        if role == 'owner':
            try:
                business = Business.objects.using('omnibiz').get(business_id=business_id, owner_id=user.user_id)
                return business is not None
            except Business.DoesNotExist:
                return False

        elif role == 'higher-staff':
            return HigherStaffAccess.objects.using('omnibiz').filter(user_id=user.user_id, business_id=business_id).exists()

        elif role == 'staff':
            return user.business_id == business_id

        elif role == 'admin':
            return False  # Admin cannot access this WebSocket

        return False  # Default to not authorized


def JWTAuthMiddlewareStack(app):
    return JWTAuthMiddleware(AuthMiddlewareStack(app))
