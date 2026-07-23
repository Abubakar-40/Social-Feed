from constance import config
from rest_framework import serializers

from posts.models import Hashtag, Post
from users.serializers import UserSerializer


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    hashtags = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True, default=0)
    comment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Post
        fields = ("id", "user", "content", "hashtags", "like_count", "comment_count", "created")

    def get_hashtags(self, post):
        hashtags = [post_hashtag.hashtag for post_hashtag in post.post_hashtags.all()]
        return HashtagSerializer(hashtags, many=True).data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "content")

    def validate_content(self, value):
        if len(value) > config.MAX_POST_LENGTH:
            raise serializers.ValidationError(f"Post content cannot exceed {config.MAX_POST_LENGTH} characters.")

        return value
