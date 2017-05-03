from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

INVALID_AUTH_TOKEN = 'INVALID_AUTH_TOKEN'
INVALID_PHONE_NUMBER = 'INVALID_PHONE_NUMBER'
INVALID_CODE_NUMBER = 'INVALID_CODE_NUMBER'
USER_NOT_FOUND = 'USER_NOT_FOUND'
USER_ALREADY_EXISTS = 'USER_ALREADY_EXISTS'


def success_response(data=None, status=None, **kwargs):
    if data is None:
        data = {}
    return Response({'data': data}, status, **kwargs)


def error_response(error_type, status, description=None, **kwargs):
    description = description or error_type
    return Response(get_error_response_content(error_type, description), status, **kwargs)


def get_error_response_content(error_type, description):
    return {
        'error': {
            'type': error_type,
            'description': description,
        }
    }


def auth_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            response.data = get_error_response_content(INVALID_AUTH_TOKEN, exc.detail)
    return response
