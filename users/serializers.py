from collections import OrderedDict

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User


class AccountSerializer(serializers.ModelSerializer):
    contacts = serializers.SerializerMethodField()

    @classmethod
    def get_contacts(cls):
        return False

    class Meta:
        model = User
        fields = ['id', 'name', 'created_at', 'phone', 'hidden_phone']
        read_only_fields = ['created_at', 'phone']


class UserIdsSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.IntegerField(), allow_empty= True)


class UserSerializer(serializers.ModelSerializer):
    contacts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'contacted']

    @classmethod
    def get_contacts(cls, obj):
        user = obj
        return user.id in cls.contacts

    def __init__(self, *args, viewer, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewer = viewer
        self.contacts = {c.user_to_ids: c for c in viewer.contacted_to.all()}
        self.blocked_viewer = set(viewer.user_blocked.all())

    def to_representation(self, instance):
        contact = self.contacts.get(instance.id)
        if contact is not None:
            data = super().to_representation(instance)
            data['name'] = contact.name
        elif self.viewer == instance:
            data = AccountSerializer(instance).data
        else:
            data = super().to_representation(instance)
            if instance.hidden_phone or instance in self.blocked_viewer:
                del data['phone']
        return data


class ImportContactsSerializer(serializers.Serializer):
    phones = serializers.ListField(child=PhoneNumberField(), allow_empty=True)
    names = serializers.ListField(child=serializers.CharField(max_length=255), allow_empty=True)

    def validate_phones(self, value):
        phones = value
        phones_unique = OrderedDict.fromkeys(phones)
        user = self.context['user']
        if len(phones_unique) != len(phones):
            raise ValidationError("Phone list contains duplicates.")
        elif user.phone in phones:
            raise ValidationError("The phones list contains user phone.")
        return list(phones_unique)

    def validate(self, attrs):
        names = attrs['names']
        phones = attrs['phones']
        if len(names) != len(phones):
            raise ValidationError("The number of phones must be equal to the number of names.")
        return attrs


class DeleteContactsSerializer(serializers.Serializer):
    phones = serializers.ListField(child=PhoneNumberField(), required=False)
    users = serializers.ListField(child=serializers.IntegerField(), required=False)