from django.urls import path

from engagements.views import (
    CommentListCreateAPIView,
    CommentRetrieveUpdateDestroyAPIView,
    ReactionToggleAPIView,
    StatsAPIView,
)


app_name = "engagements"

urlpatterns = [
    path("comments/", CommentListCreateAPIView.as_view(), name="comment-list-create"),
    path("comments/<int:pk>/", CommentRetrieveUpdateDestroyAPIView.as_view(), name="comment-retrieve-update-destroy"),
    path("reactions/", ReactionToggleAPIView.as_view(), name="reaction-toggle"),

    path("stats/", StatsAPIView.as_view(), name="stats"),
]
