import redis

from Gopchat_API import settings

client = None


def connect(fake_client=None):
    global client
    if fake_client is not None:
        client = fake_client
    else:
        client = redis.StrictRedis(host=settings.REDIS['HOST'],
                                   port=settings.REDIS['PORT'], db=settings.REDIS['DB'],
                                   password=settings.REDIS['PASSWORD'])


class CodeStorage(object):
    CODE_KEY = 'phone:{}:code'

    class DoesNotExist(Exception):
        pass

    def __init__(self, phone_number):
        self.r = client
        self.phone = phone_number
        self.code_key = self.CODE_KEY.format(phone_number)

    def get_code(self):
        code = self.r.get(self.code_key)
        if not code:
            raise self.DoesNotExist()
        return code.decode()

    def set_code(self, code):
        self.r.set(self.code_key, code)

    def delete_code(self):
        self.r.delete(self.code_key)
