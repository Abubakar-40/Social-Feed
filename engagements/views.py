from django.db.models import Count
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from engagements.models import Comment, Like
from engagements.serializers import CommentSerializer, CommentWithRepliesSerializer
from posts.models import Post
from posts.serializers import PostSerializer
from users.models import User
from users.permissions import IsOwner


class CommentListCreateAPIView(ListCreateAPIView):
    serializer_class = CommentSerializer
    search_fields = ("content",)
    ordering_fields = ("created", "like_count", "reply_count")

    def get_queryset(self):
        return Comment.objects.with_counts().filter(post_id=self.kwargs["pk"], reply_to__isnull=True)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        serializer.save(user=self.request.user, post=post)


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentWithRepliesSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return Comment.objects.with_counts()


class ReplyListCreateAPIView(ListCreateAPIView):
    serializer_class = CommentSerializer
    ordering_fields = ("created", "like_count")

    def get_queryset(self):
        return Comment.objects.with_counts().filter(reply_to_id=self.kwargs["pk"])

    def perform_create(self, serializer):
        reply_to = get_object_or_404(Comment, pk=self.kwargs["pk"])
        if reply_to.reply_to_id is not None:
            raise ValidationError("Cannot reply to a reply.")

        serializer.save(user=self.request.user, post=reply_to.post, reply_to=reply_to)


class LikeAPIView(APIView):
    model = None
    like_field = None

    def post(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, **{self.like_field: obj})

        if not created:
            like.delete()
            return Response({"liked": False}, status=status.HTTP_200_OK)

        return Response({"liked": True}, status=status.HTTP_201_CREATED)


class StatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        top_liked_posts = Post.objects.with_counts().order_by("-like_count")[:5]
        active_users = User.objects.annotate(
            post_count=Count("posts", distinct=True),
            comment_count=Count("comments", distinct=True),
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
                    "likes": Like.objects.count(),
                },
            },
            status=status.HTTP_200_OK,
        )
