from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from engagements.models import Comment
from posts.filters import PostFilter
from posts.models import Hashtag, Post
from posts.serializers import HashtagSerializer, PostCreateUpdateSerializer, PostDetailSerializer, PostSerializer
from posts.services import set_post_hashtags
from users.permissions import IsOwner


class PostListCreateAPIView(ListCreateAPIView):
    filterset_class = PostFilter
    search_fields = ("content",)
    ordering_fields = ("created", "like_count", "comment_count")

    def get_queryset(self):
        return Post.objects.with_counts()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateUpdateSerializer

        return PostSerializer

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        set_post_hashtags(post)


class PostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        replies_queryset = Comment.objects.with_counts()
        comments_queryset = (
            Comment.objects.with_counts()
            .filter(reply_to__isnull=True)
            .prefetch_related(Prefetch("replies", queryset=replies_queryset))
        )
        return Post.objects.with_counts().prefetch_related(Prefetch("comments", queryset=comments_queryset))

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PostCreateUpdateSerializer

        return PostDetailSerializer

    def perform_update(self, serializer):
        post = serializer.save()
        set_post_hashtags(post)


class HashtagListAPIView(ListAPIView):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    search_fields = ("name",)
