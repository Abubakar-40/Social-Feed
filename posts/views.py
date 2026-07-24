from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from posts.filters import PostFilter
from posts.models import Hashtag
from posts.serializers import HashtagSerializer, PostCreateUpdateSerializer, PostSerializer
from posts.utils import get_posts_queryset, sync_post_hashtags
from users.permissions import IsOwner


class PostListCreateAPIView(ListCreateAPIView):
    filterset_class = PostFilter
    search_fields = ("content",)
    ordering_fields = ("created", "like_count", "comment_count")
    ordering = ("-created",)

    def get_queryset(self):
        return get_posts_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateUpdateSerializer

        return PostSerializer

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        sync_post_hashtags(post)


class PostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return get_posts_queryset()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PostCreateUpdateSerializer

        return PostSerializer

    def perform_update(self, serializer):
        post = serializer.save()
        sync_post_hashtags(post)


class HashtagListAPIView(ListAPIView):
    queryset = Hashtag.objects.order_by("name")
    serializer_class = HashtagSerializer
    search_fields = ("name",)
