from posts.models import Hashtag, PostHashtag
from posts.utils import extract_hashtags


def set_post_hashtags(post):
    hashtag_names = extract_hashtags(post.content)
    hashtags = [Hashtag.objects.get_or_create(name=name)[0] for name in hashtag_names]

    PostHashtag.objects.filter(post=post).exclude(hashtag__in=hashtags).delete()
    for hashtag in hashtags:
        PostHashtag.objects.get_or_create(post=post, hashtag=hashtag)
