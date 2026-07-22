from django.db.models import Count, Manager, QuerySet


class CommentQuerySet(QuerySet):
    def with_counts(self):
        return self.annotate(
            like_count=Count("likes", distinct=True),
            reply_count=Count("replies", distinct=True),
        )


class CommentManager(Manager.from_queryset(CommentQuerySet)):
    def get_queryset(self):
        return super().get_queryset().select_related("user")
