import requests
from rest_framework.decorators import api_view

from Gopchat_API import settings


class SmsError(Exception):
    pass


def send_sms(phone_number, code):
    r = requests.post(settings.SMS_AUTH['REQUEST_URL'],
                      data={'To': str(phone_number), 'From': settings.SMS_AUTH['FROM_NUMBER'], 'Body': code},
                      auth=(settings.SMS_AUTH['ACCOUNT_SID'], settings.SMS_AUTH['AUTH_TOKEN']))
    if r.status_code != 201:
        raise SmsError("Service response has incorrect status code", r)

@api_view(['POST'])
def send_code(request):
