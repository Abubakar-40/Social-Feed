import re

from django.db import transaction
from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce

from engagements.models import Comment, Reaction
from posts.models import Hashtag, Post, PostHashtag


def extract_hashtags(text):
    return re.findall(r"#(\w+)", text.lower())


def sync_post_hashtags(post):
    hashtag_names = set(extract_hashtags(post.content))
    with transaction.atomic():
        existing_names = set(Hashtag.objects.filter(name__in=hashtag_names).values_list("name", flat=True))
        Hashtag.objects.bulk_create(
            [Hashtag(name=name) for name in hashtag_names - existing_names], ignore_conflicts=True
        )
        hashtag_ids = set(Hashtag.objects.filter(name__in=hashtag_names).values_list("id", flat=True))
        PostHashtag.objects.filter(post=post).exclude(hashtag_id__in=hashtag_ids).delete()
        existing_hashtag_ids = set(
            PostHashtag.objects.filter(post=post, hashtag_id__in=hashtag_ids).values_list("hashtag_id", flat=True)
        )
        PostHashtag.objects.bulk_create(
            [PostHashtag(post=post, hashtag_id=hashtag_id) for hashtag_id in hashtag_ids - existing_hashtag_ids]
        )


def get_posts_queryset():
    reaction_count_query = (
        Reaction.objects.filter(post_id=OuterRef("pk"), is_active=True)
        .order_by()
        .values("post_id")
        .annotate(total=Count("id"))
        .values("total")
    )
    comment_count_query = (
        Comment.objects.filter(post_id=OuterRef("pk"))
        .order_by()
        .values("post_id")
        .annotate(total=Count("id"))
        .values("total")
    )

    return (
        Post.objects.select_related("user")
        .prefetch_related("post_hashtags__hashtag")
        .annotate(
            like_count=Coalesce(Subquery(reaction_count_query, output_field=IntegerField()), 0),
            comment_count=Coalesce(Subquery(comment_count_query, output_field=IntegerField()), 0),
        )
    )
