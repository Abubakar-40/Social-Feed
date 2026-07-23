from django.urls import path

from engagements.models import Comment
from engagements.views import (
    CommentListCreateAPIView,
    CommentRetrieveUpdateDestroyAPIView,
    LikeAPIView,
    ReplyListCreateAPIView,
    StatsAPIView,
)
from posts.models import Post


app_name = "engagements"

urlpatterns = [
    path("<int:pk>/comments/", CommentListCreateAPIView.as_view(), name="comment-list-create"),
    path("comments/<int:pk>/",CommentRetrieveUpdateDestroyAPIView.as_view(),name="comment-retrieve-update-destroy"),

    path("comments/<int:pk>/replies/", ReplyListCreateAPIView.as_view(), name="reply-list-create"),

    path("posts/<int:pk>/like/", LikeAPIView.as_view(model=Post, like_field="post"), name="post-like"),
    path("comments/<int:pk>/like/", LikeAPIView.as_view(model=Comment, like_field="comment"), name="comment-like"),

    path("stats/", StatsAPIView.as_view(), name="stats"),
]
