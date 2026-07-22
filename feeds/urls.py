from django.urls import path

from feeds.models import Comment, Post, Reply
from feeds.views import (
    CommentListCreateAPIView,
    CommentRetrieveUpdateDestroyAPIView,
    HashtagListAPIView,
    LikeAPIView,
    PostListCreateAPIView,
    PostRetrieveUpdateDestroyAPIView,
    ReplyListCreateAPIView,
    ReplyRetrieveUpdateDestroyAPIView,
    StatsAPIView,
)


app_name = "feeds"

urlpatterns = [
    path("", PostListCreateAPIView.as_view(), name="post-list"),
    path("<int:pk>/", PostRetrieveUpdateDestroyAPIView.as_view(), name="post-detail"),

    path("<int:pk>/comments/", CommentListCreateAPIView.as_view(), name="comment-list"),
    path("comments/<int:pk>/", CommentRetrieveUpdateDestroyAPIView.as_view(), name="comment-detail"),

    path("comments/<int:pk>/replies/", ReplyListCreateAPIView.as_view(), name="reply-list"),
    path("replies/<int:pk>/", ReplyRetrieveUpdateDestroyAPIView.as_view(), name="reply-detail"),

    path("<int:pk>/like/", LikeAPIView.as_view(model=Post), name="post-like"),
    path("comments/<int:pk>/like/", LikeAPIView.as_view(model=Comment), name="comment-like"),
    path("replies/<int:pk>/like/", LikeAPIView.as_view(model=Reply), name="reply-like"),

    path("hashtags/", HashtagListAPIView.as_view(), name="hashtag-list"),
    path("stats/", StatsAPIView.as_view(), name="stats"),
]
