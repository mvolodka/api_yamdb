from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для обьектов класса Category."""
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для обьектов класса Genre."""
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGETSerializer(serializers.ModelSerializer):
    """Сериализатор для обьектов класса Title (GET)."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для обьектов класса Title."""
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
        fields = '__all__'

    def to_representation(self, title):
        """Определяет какой сериализатор выбрать."""
        serializer = TitleGETSerializer(title)
        return serializer.data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для обьектов класса User."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserCreateSerializer(serializers.Serializer):
    """Сериализатор для создания объекта класса User."""
    username = serializers.RegexField(required=True,
                                      regex=r'^[\w.@+-]',
                                      max_length=150)
    email = serializers.EmailField(required=True,
                                   max_length=254)

    def validate_username(self, username):
        """Запрещает пользователям присваивать себе имя me."""
        if username == 'me':
            raise serializers.ValidationError(
                'Использовать username "me" запрещено'
            )
        return username

    def validate(self, data):
        """Запрещает пользователям использовать повторные username и email."""
        email = data.get('email')
        username = data.get('username')
        queryset = User.objects.filter(
            Q(email=email) | Q(username=username)
        ).first()
        if queryset and (queryset.username != username
                         or queryset.email != email):
            raise serializers.ValidationError(
                'Пользователь с таким username/email уже существует'
            )
        return super().validate(data)

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        return user


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена JWT."""
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review (POST)."""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        """Запрещает пользователю на одно произведение
        оставлять более одного отзыва."""
        request = self.context.get('request')
        title = get_object_or_404(
            Title, pk=self.context.get('view').kwargs.get('title_id'))
        author = request.user
        if Review.objects.filter(
            author=author, title=title
        ).exists():
            raise serializers.ValidationError(
                'На одно произведение пользователь может'
                'оставить только один отзыв.')
        return data

    class Meta:
        model = Review
        fields = '__all__'


class ReadOnlyReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    title = serializers.SlugRelatedField(
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


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    review = serializers.SlugRelatedField(
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
