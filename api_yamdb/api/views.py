from api.filters import TitleFilter
from api.mixins import CreateRetrieveDestroyViewSet
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .permissions import IsAdmin, IsAnonymReadOnly, IsAuthor, IsModerator
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReadOnlyReviewSerializer, ReviewSerializer,
                          TitleGETSerializer, TitleSerializer,
                          UserCreateSerializer, UserSerializer)


def send_confirmation_code(username, email, confirmation_code):
    """Отправка письма с кодом подтверждения на указанный email"""
    context = {
        'username': username,
        'email': email,
        'confirmation_code': confirmation_code
    }
    message = render_to_string('send_email.txt', context)
    send_mail(
        subject='Ваш confirmation_code',
        message=message,
        from_email='YamDB@yandex.ru',
        recipient_list=[email],
        fail_silently=False,
    )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с объектами класса User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(methods=['patch', 'get'], detail=False,
            permission_classes=[IsAdmin | IsModerator | IsAuthor,
                                permissions.IsAuthenticated])
    def me(self, request):
        """Поведение объекта класса User."""
        user = request.user
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class CreateOrSignupUserViewSet(mixins.CreateModelMixin,
                                viewsets.GenericViewSet):
    """Вьюсет для авторизации/регистрации пользователей."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        """Создает или получает объект класса User и
        отправляет на почту пользователя код подтверждения."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)
        email = request.data.get('email')
        username = request.data.get('username')
        send_confirmation_code(username, email, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """Вьюсет для получения токена."""
    queryset = User.objects.all()
    serializer_class = GetTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        """Предоставляет пользователю JWT токен по коду подтверждения."""
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response('Неверный код подтверждения',
                            status=status.HTTP_400_BAD_REQUEST)
        token = AccessToken.for_user(user)
        return Response(f'Ваш токен: {token}', status=status.HTTP_200_OK)


class GenreViewSet(CreateRetrieveDestroyViewSet):
    """Вьюсет для создания объектов Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'


class CategoryViewSet(CreateRetrieveDestroyViewSet):
    """Вьюсет для создания объектов Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов Title."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = [IsAdmin | IsAnonymReadOnly]
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Определяет какой сериализатор использвать для Title."""
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания обьектов класса Review."""
    permission_classes = [IsAdmin | IsModerator | IsAuthor,
                          permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_title(self):
        """Получаем объект класса Title по title_id."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Получаем объект класса Review у объекта класса Title."""
        title = self.get_title()
        return Review.objects.select_related('author').filter(title=title)

    def perform_create(self, serializer):
        """Создаем объект класса Review у объекта класса Title."""
        serializer.save(
            author=self.request.user,
            title=self.get_title(),
        )

    def get_serializer_class(self):
        """Определяет какой сериализатор использвать для Review."""
        if self.request.method == 'POST':
            return ReviewSerializer
        return ReadOnlyReviewSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания обьектов класса Comment."""
    permission_classes = [IsAdmin | IsModerator | IsAuthor,
                          permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_review(self):
        """Получаем объект класса Review по title_id и review_id."""
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return get_object_or_404(
            Review, pk=self.kwargs.get('review_id'), title=title)

    def get_queryset(self):
        """Получаем объект класса Comment у объекта класса Review."""
        review = self.get_review()
        return Comment.objects.select_related('author').filter(review=review)

    def perform_create(self, serializer):
        """Создание объекта класса Comment у объекта класса Review."""
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
