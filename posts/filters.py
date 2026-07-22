import django_filters

from posts.models import Post


class PostFilter(django_filters.FilterSet):
    hashtag = django_filters.CharFilter(field_name="hashtags__name", lookup_expr="iexact")
    user = django_filters.NumberFilter(field_name="user__id")
    created_after = django_filters.DateTimeFilter(field_name="created", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created", lookup_expr="lte")

    class Meta:
        model = Post
        fields = ("hashtag", "user", "created_after", "created_before")
