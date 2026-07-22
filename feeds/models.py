from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from config.models import BaseModel


class Hashtag(BaseModel):
    name = models.CharField(max_length=55, unique=True)

    class Meta:
        verbose_name = "Hashtag"
        verbose_name_plural = "Hashtags"
        db_table = "hashtags"

    def __str__(self):
        return f"#{self.name}"


class Like(BaseModel):
    object_id = models.PositiveIntegerField()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="likes")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        db_table = "likes"
        unique_together = ("user", "content_type", "object_id")

    def __str__(self):
        return f"{self.user.username} likes {self.content_object}"


class Post(BaseModel):
    content = models.TextField()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="posts")
    hashtags = models.ManyToManyField("feeds.Hashtag", related_name="posts", blank=True)
    likes = GenericRelation("feeds.Like")

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        db_table = "posts"

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


class Comment(BaseModel):
    content = models.TextField()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey("feeds.Post", on_delete=models.CASCADE, related_name="comments")
    likes = GenericRelation("feeds.Like")

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        db_table = "comments"

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


class Reply(BaseModel):
    content = models.TextField()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="replies")
    comment = models.ForeignKey("feeds.Comment", on_delete=models.CASCADE, related_name="replies")
    likes = GenericRelation("feeds.Like")

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        db_table = "replies"

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
