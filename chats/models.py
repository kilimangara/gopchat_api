from django.db import models

FIELD_MAX_LENGTH = 255


class Chat(models.Model):
    title = models.CharField(max_length=FIELD_MAX_LENGTH)
    users = models.ManyToManyField("users.User", related_name="participants", through='Member')
    messages = models.ManyToManyField("Message", related_name="messages")


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
