from django.contrib import admin

from posts.models import Hashtag, Post, PostHashtag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content", "created", "is_active")
    list_filter = ("is_active", "created")
    search_fields = ("content", "user__username")


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created")
    search_fields = ("name",)


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "hashtag", "created")
    search_fields = ("post__content", "hashtag__name")
