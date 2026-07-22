from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Prefetch
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from feeds.filters import PostFilter
from feeds.models import Comment, Hashtag, Like, Post, Reply
from feeds.permissions import IsOwner
from feeds.serializers import (
    CommentSerializer,
    CommentWithRepliesSerializer,
    HashtagSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostSerializer,
    ReplySerializer,
)
from feeds.utils import annotated_comments, annotated_posts, annotated_replies, set_post_hashtags
from users.models import User


class PostListCreateAPIView(ListCreateAPIView):
    filterset_class = PostFilter
    search_fields = ("content",)
    ordering_fields = ("created", "like_count", "comment_count")

    def get_queryset(self):
        return annotated_posts()

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
        return annotated_posts().prefetch_related(Prefetch("comments", queryset=annotated_comments()))

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PostCreateUpdateSerializer

        return PostDetailSerializer

    def perform_update(self, serializer):
        post = serializer.save()
        set_post_hashtags(post)


class CommentListCreateAPIView(ListCreateAPIView):
    serializer_class = CommentSerializer
    search_fields = ("content",)
    ordering_fields = ("created", "like_count", "reply_count")

    def get_queryset(self):
        return annotated_comments().filter(post_id=self.kwargs["pk"])

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        serializer.save(user=self.request.user, post=post)


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentWithRepliesSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return annotated_comments()


class ReplyListCreateAPIView(ListCreateAPIView):
    serializer_class = ReplySerializer
    ordering_fields = ("created", "like_count")

    def get_queryset(self):
        return annotated_replies().filter(comment_id=self.kwargs["pk"])

    def perform_create(self, serializer):
        comment = get_object_or_404(Comment, pk=self.kwargs["pk"])
        serializer.save(user=self.request.user, comment=comment)


class ReplyRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReplySerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return annotated_replies()


class LikeAPIView(APIView):
    model = None

    def post(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=pk)
        content_type = ContentType.objects.get_for_model(self.model)

        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj.pk,
        )

        if not created:
            like.delete()
            return Response({"liked": False}, status=status.HTTP_200_OK)

        return Response({"liked": True}, status=status.HTTP_201_CREATED)


class HashtagListAPIView(ListAPIView):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    search_fields = ("name",)


class StatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        top_liked_posts = annotated_posts().order_by("-like_count")[:5]
        active_users = User.objects.annotate(
            post_count=Count("posts", distinct=True),
            comment_count=Count("comments", distinct=True),
            reply_count=Count("replies", distinct=True),
        ).order_by("-post_count", "-comment_count", "-reply_count")[:5]

        return Response(
            {
                "top_liked_posts": PostSerializer(top_liked_posts, many=True).data,
                "most_active_users": [
                    {
                        "username": user.username,
                        "post_count": user.post_count,
                        "comment_count": user.comment_count,
                        "reply_count": user.reply_count,
                    }
                    for user in active_users
                ],
                "totals": {
                    "posts": Post.objects.count(),
                    "comments": Comment.objects.count(),
                    "replies": Reply.objects.count(),
                    "likes": Like.objects.count(),
                },
            },
            status=status.HTTP_200_OK,
        )
