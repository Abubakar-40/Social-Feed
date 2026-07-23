from django.db import transaction
from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from engagements.choices import LikeStatus
from engagements.models import Comment, Like
from posts.filters import PostFilter
from posts.models import Hashtag, Post, PostHashtag
from posts.serializers import HashtagSerializer, PostCreateUpdateSerializer, PostSerializer
from posts.utils import extract_hashtags
from users.permissions import IsOwner


def sync_post_hashtags(post):
    hashtag_names = set(extract_hashtags(post.content))
    with transaction.atomic():
        existing_names = set(Hashtag.objects.filter(name__in=hashtag_names).values_list("name", flat=True))
        Hashtag.objects.bulk_create(
            [Hashtag(name=name) for name in hashtag_names - existing_names], ignore_conflicts=True
        )
        hashtag_ids = set(Hashtag.objects.filter(name__in=hashtag_names).values_list("id", flat=True))
        PostHashtag.objects.filter(post=post).exclude(hashtag_id__in=hashtag_ids).delete()
        existing_hashtag_ids = set(
            PostHashtag.objects.filter(post=post, hashtag_id__in=hashtag_ids).values_list("hashtag_id", flat=True)
        )
        PostHashtag.objects.bulk_create(
            [PostHashtag(post=post, hashtag_id=hashtag_id) for hashtag_id in hashtag_ids - existing_hashtag_ids]
        )

class PostListCreateAPIView(ListCreateAPIView):
    filterset_class = PostFilter
    search_fields = ("content",)
    ordering_fields = ("created", "like_count", "comment_count")

    def get_queryset(self):
        like_count_query = (
            Like.objects.filter(post_id=OuterRef("pk"), status=LikeStatus.LIKE)
            .order_by()
            .values("post_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        comment_count_query = (
            Comment.objects.filter(post_id=OuterRef("pk"))
            .order_by()
            .values("post_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        return (
            Post.objects.select_related("user")
            .prefetch_related("post_hashtags__hashtag")
            .annotate(
                like_count=Coalesce(Subquery(like_count_query, output_field=IntegerField()), 0),
                comment_count=Coalesce(Subquery(comment_count_query, output_field=IntegerField()), 0),
            )
        )

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
        like_count_query = (
            Like.objects.filter(post_id=OuterRef("pk"), status=LikeStatus.LIKE)
            .order_by()
            .values("post_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        comment_count_query = (
            Comment.objects.filter(post_id=OuterRef("pk"))
            .order_by()
            .values("post_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        return (
            Post.objects.select_related("user")
            .prefetch_related("post_hashtags__hashtag")
            .annotate(
                like_count=Coalesce(Subquery(like_count_query, output_field=IntegerField()), 0),
                comment_count=Coalesce(Subquery(comment_count_query, output_field=IntegerField()), 0),
            )
        )

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PostCreateUpdateSerializer

        return PostSerializer

    def perform_update(self, serializer):
        post = serializer.save()
        sync_post_hashtags(post)


class HashtagListAPIView(ListAPIView):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    search_fields = ("name",)
