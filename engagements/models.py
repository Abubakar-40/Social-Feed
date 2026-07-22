from django.db import models

from engagements.managers import CommentManager
from users.models import BaseModel


class Comment(BaseModel):
    content = models.TextField()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments")
    reply_to = models.ForeignKey("self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True)

    objects = CommentManager()

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        db_table = "comments"

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


class Like(BaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    comment = models.ForeignKey(
        "engagements.Comment", on_delete=models.CASCADE, related_name="likes", null=True, blank=True
    )

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        db_table = "likes"
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(post__isnull=False, comment__isnull=True)
                    | models.Q(post__isnull=True, comment__isnull=False)
                ),
                name="like_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=("user", "post"), condition=models.Q(post__isnull=False), name="unique_like_user_post"
            ),
            models.UniqueConstraint(
                fields=("user", "comment"), condition=models.Q(comment__isnull=False), name="unique_like_user_comment"
            ),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.post or self.comment}"
