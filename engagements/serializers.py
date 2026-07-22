from rest_framework import serializers

from engagements.models import Comment
from users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True, default=0)
    reply_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Comment
        fields = ("id", "user", "post", "reply_to", "content", "like_count", "reply_count", "created")
        read_only_fields = ("post", "reply_to")


class CommentWithRepliesSerializer(CommentSerializer):
    replies = CommentSerializer(many=True, read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ("replies",)
