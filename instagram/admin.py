from django.contrib import admin
from instagram.models import Post, Comment
# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'pk', 'photo']
    list_display_links = ['author']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
