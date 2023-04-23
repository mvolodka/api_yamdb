from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment, User


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserCreateSerializer(serializers.Serializer):
    username = serializers.RegexField(required=True,
                                      regex=r'^[\w.@+-]',
                                      max_length=150)
    email = serializers.EmailField(required=True,
                                   max_length=254)

    def validate_username(self, username):
        """Запрещает пользователям присваивать себе имя me
        и использовать повторные username и email."""
        if username == 'me':
            raise serializers.ValidationError(
                'Использовать username "me" запрещено'
            )
        return username

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        if (User.objects.filter(email=email).exists()
                and not User.objects.filter(username=username)):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        if (User.objects.filter(username=username).exists()
                and not User.objects.filter(email=email)):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        return data


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)


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
