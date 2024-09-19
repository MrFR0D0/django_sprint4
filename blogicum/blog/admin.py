from django.contrib import admin

from .models import Category, Location, Post

empty_value_display = 'Не задано'


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    list_filter = (
        'is_published',
        'author',
    )
    list_display_links = ('title',)
    search_fields = ('text',)


admin.site.register(Post, PostAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'is_published',
        'name',
    )
    list_editable = ('name', 'is_published')


admin.site.register(Location, LocationAdmin)
