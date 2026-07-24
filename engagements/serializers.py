from rest_framework import serializers

from engagements.models import Comment
from posts.models import Post
from users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True, default=0)
    reply_count = serializers.IntegerField(read_only=True, default=0)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "reply_to", "content", "like_count", "reply_count", "created", "user")
        read_only_fields = ("post", "reply_to")


class CommentCreateSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ("id", "content", "post", "reply_to")
        read_only_fields = ("id",)

    def validate(self, attrs):
        post = attrs["post"]
        reply_to = attrs.get("reply_to")

        if reply_to and reply_to.post_id != post.id:
            raise serializers.ValidationError("The parent comment must belong to the selected post.")

        if reply_to and reply_to.reply_to_id is not None:
            raise serializers.ValidationError("Cannot reply to a reply.")

        return attrs


class CommentWithRepliesSerializer(CommentSerializer):
    replies = CommentSerializer(many=True, read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ("replies",)


class ReactionSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(choices=("post", "comment"))
    target_id = serializers.IntegerField(min_value=1)
