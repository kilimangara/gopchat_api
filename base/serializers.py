from rest_framework import serializers


class ForeignUserIdSerializer(serializers.Serializer):
    user = serializers.IntegerField()

    def validate_user(self, value):
        viewer = self.context['viewer']
        if viewer.id == value:
            raise serializers.ValidationError("Can not do it with yourself.")
        return value
