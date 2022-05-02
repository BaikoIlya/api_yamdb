from django.contrib import admin

from .models import Category, Genre, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка отображения модели(Category) в админке."""

    list_display = (
        'pk',
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Настройка отображения модели(Genre) в админке."""

    list_display = (
        'pk',
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Настройка отображения модели(Title) в админке."""

    list_display = (
        'pk',
        'name',
        'year',
        'description',
    )
    search_fields = (
        'name',
        'year',
    )
    empty_value_display = '-пусто-'
