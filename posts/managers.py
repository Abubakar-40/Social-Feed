from django.db.models import Count, Manager, QuerySet


class PostQuerySet(QuerySet):
    def with_counts(self):
        return self.annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        )


class PostManager(Manager.from_queryset(PostQuerySet)):
    def get_queryset(self):
        return super().get_queryset().select_related("user").prefetch_related("hashtags")
