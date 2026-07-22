import re

from django.db.models import Count, Prefetch

from feeds.models import Comment, Hashtag, Post, Reply


def extract_hashtags(text):
    return re.findall(r"#(\w+)", text.lower())


def set_post_hashtags(post):
    hashtag_names = extract_hashtags(post.content)
    hashtags = [Hashtag.objects.get_or_create(name=name)[0] for name in hashtag_names]
    post.hashtags.set(hashtags)


def annotated_replies():
    return Reply.objects.select_related("user").annotate(like_count=Count("likes", distinct=True))


def annotated_comments():
    return (
        Comment.objects.select_related("user")
        .prefetch_related(Prefetch("replies", queryset=annotated_replies()))
        .annotate(
            like_count=Count("likes", distinct=True),
            reply_count=Count("replies", distinct=True),
        )
    )


def annotated_posts():
    return (
        Post.objects.select_related("user")
        .prefetch_related("hashtags")
        .annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        )
    )
