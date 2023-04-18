from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=100)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Категория', max_length=100)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=100)
    year = models.PositiveSmallIntegerField('Год выпуска')
    description = models.TextField('Описание')
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='genretitles',
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        related_name='genretitles',
    )

    class Meta:
        ordering = ('genre',)

    def __str__(self):
        return f'Произведение: {self.title}, жанр:{self.genre}'
