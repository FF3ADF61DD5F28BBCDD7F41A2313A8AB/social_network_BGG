from django.contrib import admin
from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

admin.site.register(Post, PostAdmin)


class GroupsAdmin(admin.ModelAdmin):
    list_display =('title', 'slug', 'description')
    search_fields = ('title', 'description')
    empty_value_display = '-пусто-'

admin.site.register(Group, GroupsAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created')
    search_fields = ('text', 'author')
    list_filter = ('created',)

admin.site.register(Comment, CommentAdmin)