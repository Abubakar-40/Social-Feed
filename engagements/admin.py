from django.contrib import admin

from engagements.models import Comment, Reaction


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "reply_to", "content", "created", "is_active")
    list_filter = ("is_active", "created")
    search_fields = ("content", "user__username")


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "comment", "is_active", "created")
    search_fields = ("user__username",)
