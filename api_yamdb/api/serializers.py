from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Comment, Review, Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        read_only_fields = ('title',)
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('title', 'author')
            )
        ]

    def validate(self, data):
        author = self.context.get('request').user
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))

        if Review.objects.filter(
            author=author, title=title
        ).exists():
            raise serializers.ValidationError(
                'На одно произведение пользователь может'
                'оставить только один отзыв.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        read_only_fields = ('review',)
        fields = '__all__'
