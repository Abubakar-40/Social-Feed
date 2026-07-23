from django.db import models


class LikeStatus(models.TextChoices):
    LIKE = "LIKE", "Like"
    UNLIKE = "UNLIKE", "Unlike"
