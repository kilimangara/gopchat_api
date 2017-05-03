import requests
from rest_framework import status
from rest_framework.decorators import api_view

from Gopchat_API import settings
from authtoken import token
from registration.code_storage import CodeStorage
from registration.serializers import PhoneSerializer, CodeSerializer, NewUserSerializer, IsNewSerializer
from base.responses import error_response, success_response, INVALID_PHONE_NUMBER, INVALID_CODE_NUMBER, USER_ALREADY_EXISTS, USER_NOT_FOUND
from users.models import User


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
    phone_serializer = PhoneSerializer(data=request.data)
    if not phone_serializer.is_valid():
        return error_response(INVALID_PHONE_NUMBER, status.HTTP_400_BAD_REQUEST, phone_serializer.errors_as_text)
    phone_number = phone_serializer.validated_data['phone']
    phone_storage = CodeStorage(phone_number)
    code = CodeSerializer.generate_code()
    phone_storage.set_code(code)
    send_sms(phone_number, code)
    is_new = not User.objects.filter(phone=phone_number).exists()
    return success_response({'is_new': is_new}, status.HTTP_201_CREATED)


def check_is_new(request):
    is_new_serializer = IsNewSerializer(data=request.data)
    if not is_new_serializer.is_valid():
        return False
    return is_new_serializer.validated_data['is_new']


@api_view(['POST'])
def login(request):
    phone_serializer = PhoneSerializer(data=request.data)
    phone_serializer.is_valid(raise_exception=True)
    code_serializer = CodeSerializer(data=request.data)
    if not code_serializer.is_valid():
        return error_response(INVALID_CODE_NUMBER, status.HTTP_400_BAD_REQUEST, code_serializer.errors_as_text)
    phone_number = phone_serializer.validated_data['phone']
    code = code_serializer.validated_data['code']
    phone_storage = CodeStorage(phone_number)
    if code != settings.SMS_AUTH['DEBUG_CODE']:
        real_code = phone_storage.get_code()
        if code != real_code:
            return error_response(INVALID_CODE_NUMBER, status.HTTP_400_BAD_REQUEST, "Incorrect code")
    if not check_is_new(request):
        try:
            user_id = User.objects.only('id').get(phone=phone_number).id
        except User.DoesNotExist:
            return error_response(USER_NOT_FOUND, status.HTTP_404_NOT_FOUND,
                                  "There is no such user registered via this phone")
    else:
        user_serializer = NewUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        if User.objects.filter(phone=phone_number).exists():
            return error_response(USER_ALREADY_EXISTS, status.HTTP_409_CONFLICT,
                                  "This phone has already used by another user")
        user_id = user_serializer.save().id
    auth_token = token.create(user_id)
    phone_storage.delete_code()
    return success_response({'token': auth_token, 'user_id':user_id}, status.HTTP_201_CREATED)