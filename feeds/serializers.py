from constance import config
from rest_framework import serializers

from feeds.models import Comment, Hashtag, Post, Reply
from users.serializers import UserSerializer


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Reply
        fields = ("id", "user", "comment", "content", "like_count", "created")
        read_only_fields = ("comment",)


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True, default=0)
    reply_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Comment
        fields = ("id", "user", "post", "content", "like_count", "reply_count", "created")
        read_only_fields = ("post",)


class CommentWithRepliesSerializer(CommentSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ("replies",)


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True, default=0)
    comment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Post
        fields = ("id", "user", "content", "hashtags", "like_count", "comment_count", "created")


class PostDetailSerializer(PostSerializer):
    comments = CommentWithRepliesSerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ("comments",)


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "content")

    def validate_content(self, value):
        if len(value) > config.MAX_POST_LENGTH:
            raise serializers.ValidationError(f"Post content cannot exceed {config.MAX_POST_LENGTH} characters.")

        return value
