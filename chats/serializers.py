from rest_framework import serializers

from chats.models import Chat, Member, Message


class ChatsSerializer(serializers.ModelSerializer):
    king = serializers.SerializerMethodField(read_only=True)

    @classmethod
    def get_king(cls, obj):
        return cls.context.get('king_id') or obj.king_id

    def create(self, validated_data):
        model = super().create(validated_data)
        user_ids = self.context['user_ids']
        king_id = self.context['king_id']
        members = [Member(user_id=uid, chat=model,king=uid == king_id) for uid in user_ids]
        Member.objects.bulk_create(members)
        return model

    class Meta:
        model = Chat
        field = ['id', 'title', 'users', 'king', 'messages']


class MessageSerializer(serializers.ModelSerializer):

    def __init__(self, *args, sender , **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender

    def create(self, validated_data):
        chat_id = self.context['chat_id']
        message = self.context['message']
        from_id = self.sender.id
        model = Message(msg_from=from_id, text=message, chat_id=chat_id)
        Message.objects.create(model)

    class Meta:
        model = Message
        field = ['msg_from', 'text', 'created_at', 'is_checked']
        read_only_field = ['is_checked', 'created_at']
