from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Comment, Review, Title


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('title', 'author')
            )
        ]

    def validate(self, data):
        title = get_object_or_404(
            Title, pk=self.context.get('view').kwargs.get('title_id'))
        request = self.context.get('request')
        author = request.user

        if request.method == 'POST':
            if Review.objects.filter(
                author=author, title=title
            ).exists():
                raise serializers.ValidationError(
                    'На одно произведение пользователь может'
                    'оставить только один отзыв.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
