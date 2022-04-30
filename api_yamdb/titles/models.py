from django.db import models

from .validators import validator_year


class Category(models.Model):
    """Модель для категорий произведений."""
    name = models.CharField(
        max_length=200,
        verbose_name='category name',
        help_text='Категория, к которой относится произведение',
        db_index=True,
    )
    slug = models.SlugField(
        unique=True,
        help_text='Уникальный URL категории',
    )

    class Meta:
        ordering = [
            'name',
        ]
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name[:15]


class Genre(models.Model):
    """Модель для жанров произведений."""
    name = models.CharField(
        max_length=200,
        verbose_name='genre name',
        help_text='Жанр, к которому относится произведение',
        db_index=True
    )
    slug = models.SlugField(
        unique=True,
        help_text='Уникальный URL жанра',
    )

    class Meta:
        ordering = [
            'name',
        ]
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name[:15]


class Title(models.Model):
    """Модель для названий произведений."""
    name = models.CharField(
        max_length=200,
        verbose_name='title name',
        help_text='Уникальное название произведения',
    )
    year = models.IntegerField(
        null=True,
        blank=True,
        validators=[validator_year],
        verbose_name='year creation',
        help_text='Год создания произведения',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='category',
        help_text='Категория к которой относится произведение',
    )
    description = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='description',
        help_text='Описание произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='genre',
        help_text='Жанр которой относится произведение',
    )

    class Meta:
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name[:15]


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.genre} {self.title}'
