from django.urls import path

from posts.views import HashtagListAPIView, PostListCreateAPIView, PostRetrieveUpdateDestroyAPIView


app_name = "posts"

urlpatterns = [
    path("", PostListCreateAPIView.as_view(), name="post-list-create"),
    path("<int:pk>/", PostRetrieveUpdateDestroyAPIView.as_view(), name="post-retrieve-update-destroy"),

    path("hashtags/", HashtagListAPIView.as_view(), name="hashtag-list"),
]
