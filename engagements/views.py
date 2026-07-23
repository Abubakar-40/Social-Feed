from django.db.models import Count, IntegerField, OuterRef, Prefetch, Subquery
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from engagements.choices import LikeStatus
from engagements.models import Comment, Like
from engagements.serializers import CommentSerializer, CommentWithRepliesSerializer
from posts.models import Post
from posts.serializers import PostSerializer
from users.models import User
from users.permissions import IsOwner


class CommentListCreateAPIView(ListCreateAPIView):
    parent_type = None
    serializer_class = CommentSerializer
    search_fields = ("content",)
    ordering_fields = ("created", "like_count", "reply_count")

    def get(self, request, *args, **kwargs):
        if self.parent_type == "comment":
            return self.http_method_not_allowed(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        like_count_query = (
            Like.objects.filter(comment_id=OuterRef("pk"), status=LikeStatus.LIKE)
            .order_by()
            .values("comment_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        reply_count_query = (
            Comment.objects.filter(reply_to_id=OuterRef("pk"))
            .order_by()
            .values("reply_to_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        return (
            Comment.objects.select_related("user")
            .filter(post_id=self.kwargs["pk"], reply_to__isnull=True)
            .annotate(
                like_count=Coalesce(Subquery(like_count_query, output_field=IntegerField()), 0),
                reply_count=Coalesce(Subquery(reply_count_query, output_field=IntegerField()), 0),
            )
        )

    def perform_create(self, serializer):
        if self.parent_type == "post":
            post = get_object_or_404(Post, pk=self.kwargs["pk"])
            serializer.save(user=self.request.user, post=post)
            return

        parent_comment = get_object_or_404(Comment, pk=self.kwargs["pk"])
        if parent_comment.reply_to_id is not None:
            raise ValidationError("Cannot reply to a reply.")

        serializer.save(user=self.request.user, post=parent_comment.post, reply_to=parent_comment)


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentWithRepliesSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        like_count_query = (
            Like.objects.filter(comment_id=OuterRef("pk"), status=LikeStatus.LIKE)
            .order_by()
            .values("comment_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        reply_count_query = (
            Comment.objects.filter(reply_to_id=OuterRef("pk"))
            .order_by()
            .values("reply_to_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        replies_queryset = Comment.objects.select_related("user").annotate(
            like_count=Coalesce(Subquery(like_count_query, output_field=IntegerField()), 0),
            reply_count=Coalesce(Subquery(reply_count_query, output_field=IntegerField()), 0),
        )
        return (
            Comment.objects.select_related("user")
            .annotate(
                like_count=Coalesce(Subquery(like_count_query, output_field=IntegerField()), 0),
                reply_count=Coalesce(Subquery(reply_count_query, output_field=IntegerField()), 0),
            )
            .prefetch_related(Prefetch("replies", queryset=replies_queryset))
        )


class LikeAPIView(APIView):
    model = None
    like_field = None

    def post(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=pk)
        like, created = Like.objects.get_or_create(
            user=request.user,
            defaults={"status": LikeStatus.LIKE},
            **{self.like_field: obj},
        )

        if not created:
            like.status = LikeStatus.UNLIKE if like.status == LikeStatus.LIKE else LikeStatus.LIKE
            like.save(update_fields=("status", "modified"))
            return Response({"liked": like.status == LikeStatus.LIKE}, status=status.HTTP_200_OK)

        return Response({"liked": True}, status=status.HTTP_201_CREATED)


class StatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
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
        top_liked_posts = (
            Post.objects.select_related("user")
            .prefetch_related("post_hashtags__hashtag")
            .annotate(
                like_count=Coalesce(Subquery(like_count_query, output_field=IntegerField()), 0),
                comment_count=Coalesce(Subquery(comment_count_query, output_field=IntegerField()), 0),
            )
            .order_by("-like_count")[:5]
        )
        post_count_query = (
            Post.objects.filter(user_id=OuterRef("pk"))
            .order_by()
            .values("user_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        user_comment_count_query = (
            Comment.objects.filter(user_id=OuterRef("pk"))
            .order_by()
            .values("user_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        active_users = User.objects.annotate(
            post_count=Coalesce(Subquery(post_count_query, output_field=IntegerField()), 0),
            comment_count=Coalesce(Subquery(user_comment_count_query, output_field=IntegerField()), 0),
        ).order_by("-post_count", "-comment_count")[:5]

        return Response(
            {
                "top_liked_posts": PostSerializer(top_liked_posts, many=True).data,
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
                    "likes": Like.objects.filter(status=LikeStatus.LIKE).count(),
                },
            },
            status=status.HTTP_200_OK,
        )
