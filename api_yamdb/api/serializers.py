from django.db.models import Avg
from rest_framework import serializers
from reviews.models import Category, Genre, Title, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGETSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Title
        exclude = ('id',)

    def get_rating(self, obj):
        rating = Review.objects.filter(
            title=obj.id
        ).aggregate(Avg('score'))['score__avg']
        if rating is not None:
            return round(rating)
        return None


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        exclude = ('id',)

    def to_representation(self, title):
        serializer = TitleGETSerializer(title)
        return serializer.data
