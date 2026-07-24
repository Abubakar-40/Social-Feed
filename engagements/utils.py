from django.db.models import Count, IntegerField, OuterRef, Prefetch, Subquery
from django.db.models.functions import Coalesce
from rest_framework.exceptions import ValidationError

from engagements.models import Comment, Reaction
from posts.models import Post
from users.models import User
from posts.utils import get_posts_queryset


def get_comments_queryset(include_replies=False):
    reaction_count_query = (
        Reaction.objects.filter(comment_id=OuterRef("pk"), is_active=True)
        .order_by()
        .values("comment_id")
        .annotate(total=Count("id"))
        .values("total")
    )
    reply_count_query = (
        Comment.objects.filter(reply_to_id=OuterRef("pk"))
        .order_by()
        .values("reply_to_id")
        .annotate(total=Count("id"))
        .values("total")
    )
    queryset = Comment.objects.select_related("user").annotate(
        like_count=Coalesce(Subquery(reaction_count_query, output_field=IntegerField()), 0),
        reply_count=Coalesce(Subquery(reply_count_query, output_field=IntegerField()), 0),
    )

    if include_replies:
        replies_queryset = Comment.objects.select_related("user").annotate(
            like_count=Coalesce(Subquery(reaction_count_query, output_field=IntegerField()), 0),
            reply_count=Coalesce(Subquery(reply_count_query, output_field=IntegerField()), 0),
        )
        queryset = queryset.prefetch_related(Prefetch("replies", queryset=replies_queryset))

    return queryset


def toggle_reaction(user, target_type, target_id):
    target_models = {
        "post": (Post, "post"),
        "comment": (Comment, "comment"),
    }
    model, field_name = target_models[target_type]
    target = model.objects.filter(pk=target_id).first()
    if target is None:
        raise ValidationError({"target_id": "The selected target does not exist."})

    reaction, created = Reaction.objects.get_or_create(
        user=user,
        defaults={"is_active": True},
        **{field_name: target},
    )
    if not created:
        reaction.is_active = not reaction.is_active
        reaction.save(update_fields=("is_active", "modified"))

    return reaction.is_active, created


def get_top_reacted_posts():
    return get_posts_queryset().order_by("-like_count")[:5]


def get_most_active_users():
    post_count_query = (
        Post.objects.filter(user_id=OuterRef("pk"))
        .order_by()
        .values("user_id")
        .annotate(total=Count("id"))
        .values("total")
    )
    comment_count_query = (
        Comment.objects.filter(user_id=OuterRef("pk"))
        .order_by()
        .values("user_id")
        .annotate(total=Count("id"))
        .values("total")
    )

    return User.objects.annotate(
        post_count=Coalesce(Subquery(post_count_query, output_field=IntegerField()), 0),
        comment_count=Coalesce(Subquery(comment_count_query, output_field=IntegerField()), 0),
    ).order_by("-post_count", "-comment_count")[:5]
