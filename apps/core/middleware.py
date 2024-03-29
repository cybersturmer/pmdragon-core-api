from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import decode as jwt_decode, InvalidTokenError

from libs.exception.websocket import NoTokenError

User = get_user_model()


class JWTAuthMiddleware:
    def __init__(self, application):
        self.application = application

    @database_sync_to_async
    def get_user_by_id(self, user_id: int):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

    @staticmethod
    def get_token_from_scope(scope):
        query_string = parse_qs(scope.get('query_string').decode('utf-8'))
        token_list = query_string.get('token', None)

        if token_list is None or len(token_list) < 1:
            raise NoTokenError

        return token_list.pop()

    async def __call__(self, scope: dict, receive, send):
        close_old_connections()

        try:
            token = self.get_token_from_scope(scope)

            token_data = jwt_decode(token,
                                    settings.SECRET_KEY,
                                    algorithms=settings.SIMPLE_JWT.get('ALGORITHM'))

            user_id = token_data.get('user_id')
            scope['user'] = await self.get_user_by_id(user_id=user_id)

        except (NoTokenError,
				InvalidTokenError,
                KeyError) as e:
            scope['user'] = AnonymousUser()
            print(f'JWTAuthMiddleware: {e.__class__.__name__}')

        return await self.application(scope, receive, send)
