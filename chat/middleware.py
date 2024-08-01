from urllib.parse import parse_qs
# from channels.middleware.base import BaseMiddleware 
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model


User = get_user_model()

@database_sync_to_async
def get_user(token):
    try:
        user_id = UntypedToken(token).payload['user_id']
    
        return User.objects.get(id = user_id)
   
    except Exception as e:
        print(e)
        return AnonymousUser()


def get_accesstoken_from_scope(scope):
  
    cookie_header = None
    for key, value in scope['headers']:
        if key == b'cookie':
            cookie_header = value.decode('utf-8')
            break

    # Step 2: Parse the cookie header to extract the access token
    access_token = None
    if cookie_header:
        cookies = cookie_header.split('; ')
        for cookie in cookies:
            if cookie.startswith('access='):
                access_token = cookie.split('=')[1]
                break
    return access_token


    
class TokenAuthMiddleware(BaseMiddleware):

    async def __call__(self,scope,receive,send):
        t = get_accesstoken_from_scope(scope)
        if t:
            user = await get_user(t)
            scope["user"] = user
        else:
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)
    

