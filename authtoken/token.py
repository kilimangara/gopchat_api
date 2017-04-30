import binascii
import os

import redis

from Gopchat_API import settings

client = None


def connect(fake_client=None):
    global client
    if fake_client is not None:
        client = fake_client
    else:
        client = redis.StrictRedis(host=settings.REDIS['HOST'], port=settings.REDIS['PORT'], password=settings.REDIS['PASSWORD'],
                                   db=settings.REDIS['DB'])


class TokenDoesNotExist(Exception):
    pass


class AuthenticationFailed(Exception):
    pass


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


def format_token_request(token):
    return 'token:{}'.format(token)


def format_user_id(user_id):
    return 'user:{}'.format(user_id)


def authenticate(token):
    token_key = format_token_request(token)
    user_id = int(client.get(token_key) or 0)
    if not user_id:
        raise AuthenticationFailed()
    return user_id


def create(user_id):
    user_key = format_user_id(user_id)
    token = generate_token()
    token_key = format_token_request(token)
    pipe = client.pipeline()
    pipe.set(user_key, token)
    pipe.set(token_key, user_id)
    pipe.execute()
    return token


def delete(user_id):
    user_key = format_user_id(user_id)
    token = (client.get(user_key) or b'').decode()
    if not token:
        raise TokenDoesNotExist()
    return token


connect()
