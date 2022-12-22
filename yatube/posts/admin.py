from django.contrib import admin
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
        'image',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)