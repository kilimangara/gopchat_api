from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

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


@receiver(post_save, sender=User)
def new_user(instance, created, **kwargs):
    if not created:
        return
    Contacts.objects.filter(phone=instance.phone).update(contacted=instance)


class Contacts(models.Model):
    contacted = models.ForeignKey("User", models.SET_NULL,related_name="contacted_to", null=True)
    contacted_by = models.ForeignKey("User",models.CASCADE, related_name="contacted_from")
    phone = PhoneNumberField()
    name = models.CharField(max_length=FIELD_MAX_LENGTH, null=True)

    class Meta:
        unique_together = ['contacted', 'contacted_by']


class BlackList(models.Model):
    blocked = models.ForeignKey("User", related_name="blocked_to")
    blocked_by = models.ForeignKey("User", related_name="blocked_from")

    class Meta:
        unique_together = ['blocked', 'blocked_by']
