from django.db import models
from phonenumber_field.formfields import PhoneNumberField

FIELD_MAX_LENGTH = 255


class User(models.Model):
    name = models.CharField(max_length=FIELD_MAX_LENGTH)
    phone = PhoneNumberField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hidden_phone = models.BooleanField(default=False)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone'
