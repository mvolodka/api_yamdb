from django.contrib import admin

from django.db.models import Avg


from .models import Category, Comment, Genre, GenreTitle, Review, Title, User


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'text',
        'author',
        'pub_date',
        'score',
    )
    search_fields = ('title',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )
    list_editable = ('role',)
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'


class GenreTitleInline(admin.TabularInline):
    model = GenreTitle
    extra = 1


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    inlines = (
        GenreTitleInline,
    )
    list_display = (
        'pk',
        'name',
        'year',
        'description',
        'category',
        'get_rating',
    )
    list_editable = ('category',)
    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = '-пусто-'

    def get_rating(self, obj):
        """Получаем среднюю оценку произведения по оценкам пользователей"""
        rating = Review.objects.filter(
            title=obj.id
        ).aggregate(Avg('score'))['score__avg']
        if rating is not None:
            return round(rating)
        return None

    get_rating.short_description = 'Рейтинг'

