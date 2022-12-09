from django.contrib import admin

from .models import Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group', )
    search_fields = ('text', )
    list_filter = ('created', 'group', )
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'slug',
        'title',
        'description',
    )
    search_fields = ('title', 'description',)
    empty_value_display = '-пусто-'
