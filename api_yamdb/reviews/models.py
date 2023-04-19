from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    ...


class Title(models.Model):
    ...


class Review(models.Model):
    # id,title_id,text,author,score,pub_date - поля из csv
    # for test api
    # title = models.IntegerField(default=1)
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Отзыв'),
        help_text=_('Отзыв к произведению')
    )
    text = models.TextField(
        verbose_name=_('Текст отзыва'),
        help_text=_('Введите текст отзыва'),
        blank=False
    )
    # for test api
    # author = models.IntegerField(default=1)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Автор отзыва')
    )
    score = models.IntegerField(
        verbose_name=_('Рейтинг произведения'),
        help_text=_('Введите значение от 1 до 10'),
        blank=False
    )
    pub_date = models.DateTimeField(
        verbose_name=_('Дата публикации'),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(score_gte=1) & models.Q(score_lt=10),
                name='Значение рейтинга произведения допустимо'
                     'в диапозоне от 1 до 10',
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique review')
        ]
        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    # id,reiew_id,text,author,pub_date - поля из csv
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Отзыв'),
        help_text=_('Отзыв к произведению')
    )
    text = models.TextField(
        verbose_name=_('Текст комментария'),
        help_text=_('Введите текст комментария'),
        blank=False
    )
    # for test api
    # author = models.IntegerField(default=1)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Автор комментария')
    )
    pub_date = models.DateTimeField(
        verbose_name=_('Дата публикации'),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]
