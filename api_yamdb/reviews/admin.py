from django.contrib import admin

from .models import Review, Comment
from api_yamdb.settings import EMPTY_VALUE_DISPLAY


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'author',)
    search_fields = ('author',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'review',)
    search_fields = ('author',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_VALUE_DISPLAY
