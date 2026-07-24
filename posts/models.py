from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from users.models import BaseModel


class Hashtag(BaseModel):
    name = models.CharField(max_length=55, unique=True)

    class Meta:
        verbose_name = "Hashtag"
        verbose_name_plural = "Hashtags"
        db_table = "hashtags"

    def __str__(self):
        return f"#{self.name}"


class Post(BaseModel):
    content = CKEditor5Field()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="posts")

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        db_table = "posts"

    def __str__(self):
        return self.user.username


class PostHashtag(BaseModel):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="post_hashtags")
    hashtag = models.ForeignKey("posts.Hashtag", on_delete=models.CASCADE, related_name="post_hashtags")

    class Meta:
        verbose_name = "Post Hashtag"
        verbose_name_plural = "Post Hashtags"
        db_table = "post_hashtags"
        unique_together = ("post", "hashtag")

    def __str__(self):
        return f"{self.post_id} - #{self.hashtag.name}"
