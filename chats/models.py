import random

from django.db import models
from django.db.transaction import atomic

from users.models import User

FIELD_MAX_LENGTH = 255


class Chat(models.Model):
    title = models.CharField(max_length=FIELD_MAX_LENGTH)
    users = models.ManyToManyField("users.User", related_name="participants", through='Member')
    messages = models.ManyToManyField("Message", related_name="messages")

    @property
    def king_id(self):
        return User.objects.filter(members__chat=self, members__king=True).values_list('id', flat=True).first()

    def add_user(self, user_id):
        _, created = self.chats.get_or_create(user_id=user_id)
        return created

    def remove_user(self, user_id):
        chat_exist = True
        with atomic():
            if self.chats.filter(user_id=user_id, king=True).exists():
                user_ids = self.chats.exclude(user_id=user_id).values_list('id', flat=True)
                if user_ids:
                    new_king_id = random.choice(user_ids)
                    self.chats.filter(user_id=new_king_id).update(king=True)
                deleted = self.chats.filter(user_id=user_id).delete()
                removed = bool(deleted)
                if not self.chats.exists():
                    self.delete()
                    chat_exist = False
        return removed, chat_exist


class Message(models.Model):
    msg_from = models.ForeignKey("users.User", related_name='author')
    msg_to = models.ForeignKey("Chat", related_name='receiver')
    text = models.CharField(max_length=FIELD_MAX_LENGTH)
    created_at = models.DateTimeField(auto_now_add=True)
    is_checked = models.BooleanField(default=False)


class Member(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="members")
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, related_name="chats")
    king = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'chat']
