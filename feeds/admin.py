from django.contrib import admin

from feeds.models import Comment, Hashtag, Like, Post, Reply


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content", "created", "is_active")
    list_filter = ("is_active", "created")
    search_fields = ("content", "user__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "content", "created", "is_active")
    list_filter = ("is_active", "created")
    search_fields = ("content", "user__username")


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "content", "created", "is_active")
    list_filter = ("is_active", "created")
    search_fields = ("content", "user__username")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content_type", "object_id", "created")
    list_filter = ("content_type",)
    search_fields = ("user__username",)


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created")
    search_fields = ("name",)
