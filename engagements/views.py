from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from engagements.models import Comment, Reaction
from engagements.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    CommentWithRepliesSerializer,
    ReactionSerializer,
)
from engagements.utils import (
    get_comments_queryset,
    get_most_active_users,
    get_top_reacted_posts,
    toggle_reaction,
)
from posts.models import Post
from posts.serializers import PostSerializer
from users.permissions import IsOwner


class CommentListCreateAPIView(ListCreateAPIView):
    search_fields = ("content",)
    ordering_fields = ("created", "like_count", "reply_count")
    ordering = ("-created",)

    def get_queryset(self):
        post_id = self.request.query_params.get("post_id")
        if post_id is None:
            raise ValidationError({"post_id": "This query parameter is required."})

        return get_comments_queryset().filter(post_id=post_id, reply_to__isnull=True)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer

        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return get_comments_queryset(include_replies=True)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CommentSerializer

        return CommentWithRepliesSerializer


class ReactionToggleAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_active, created = toggle_reaction(request.user, **serializer.validated_data)

        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK

        return Response({"liked": is_active}, status=response_status)


class StatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        top_reacted_posts = get_top_reacted_posts()
        active_users = get_most_active_users()

        return Response(
            {
                "top_liked_posts": PostSerializer(top_reacted_posts, many=True).data,
                "most_active_users": [
                    {
                        "username": user.username,
                        "post_count": user.post_count,
                        "comment_count": user.comment_count,
                    }
                    for user in active_users
                ],
                "totals": {
                    "posts": Post.objects.count(),
                    "comments": Comment.objects.count(),
                    "likes": Reaction.objects.filter(is_active=True).count(),
                },
            },
            status=status.HTTP_200_OK,
        )
