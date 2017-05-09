from collections import Iterable

from bulk_update.helper import bulk_update
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.db.transaction import atomic
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

from authtoken import token

FIELD_MAX_LENGTH = 255


class User(models.Model):
    name = models.CharField(max_length=FIELD_MAX_LENGTH)
    phone = PhoneNumberField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hidden_phone = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    contacted_users = models.ManyToManyField('self', related_name="user_contacted", through="Contacts",
                                             symmetrical=False, through_fields=['contacted', 'contacted_by'])
    blocked_users = models.ManyToManyField('self', related_name="user_blocked", through="BlackList", symmetrical=False,
                                           through_fields=['blocked', 'blocked_by'])
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone'

    def __str__(self):
        return '{} {}'.format(self.phone, self.id)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def remove_from_blacklist(self, user_id):
        self.blocks.filter(blocked_to_id=user_id).delete()

    def add_to_contacts(self, phones, names):
        if isinstance(phones, Iterable) and not isinstance(phones, str):
            input_contacts = dict(zip(phones, names))
        else:
            # if single contact
            input_contacts = {phones: names}
        old_contacts = self.contacts.filter(phone__in=input_contacts.keys())
        contacted_user_ids = []
        for contact in old_contacts:
            phone = contact.phone
            contact.name = input_contacts[phone]
            input_contacts.pop(phone)
            if contact.user_to_id is not None:
                contacted_user_ids.append(contact.user_to_id)
        registered_phones = dict(User.objects.filter(phone__in=input_contacts.keys()).values_list('phone', 'id'))
        to_create = []
        for phone, name in input_contacts.items():
            user_to_id = registered_phones.get(phone, None)
            c = Contacts(contacted_from=self, contacted_to_id=user_to_id, phone=phone, name=name)
            to_create.append(c)
            if user_to_id is not None:
                contacted_user_ids.append(c.user_to_id)
        with atomic():
            bulk_update(old_contacts, update_fields=['name'])
            Contacts.objects.bulk_create(to_create)
        return User.objects.filter(id__in=contacted_user_ids)


@receiver(pre_delete, sender=User)
def delete_user(instance, **kwargs):
    token.delete(instance.id)


@receiver(post_save, sender=User)
def new_user(instance, created, **kwargs):
    if not created:
        return
    Contacts.objects.filter(phone=instance.phone).update(contacted=instance)


class Contacts(models.Model):
    contacted = models.ForeignKey("User", models.SET_NULL, related_name="contacted_to", null=True)
    contacted_by = models.ForeignKey("User", models.CASCADE, related_name="contacted_from")
    phone = PhoneNumberField()
    name = models.CharField(max_length=FIELD_MAX_LENGTH, null=True)

    class Meta:
        unique_together = ['contacted', 'contacted_by']


class BlackList(models.Model):
    blocked = models.ForeignKey("User", models.CASCADE, related_name="blocked_to")
    blocked_by = models.ForeignKey("User", models.CASCADE, related_name="blocked_from")

    class Meta:
        unique_together = ['blocked', 'blocked_by']
