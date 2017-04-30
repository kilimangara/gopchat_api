
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from authtoken import token
from users.models import User


class RedisTokenAuthentication(TokenAuthentication):
    @classmethod
    def authenticate_credentials(cls, key):
        try:
            user_id = token.authenticate(key)
            user = User.objects.get(pk=user_id)
        except(token.AuthenticationFailed, User.DoesNotExist):
            raise AuthenticationFailed()
        return user, key
