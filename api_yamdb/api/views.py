from api.mixins import CreateRetrieveDestroyViewSet
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User

from .permissions import SuperUserOrAdmin, SuperUserOrAdminOrModeratorOrAuthor
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, TitleGETSerializer,
                          TitleSerializer, UserCreateSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с объектами класса User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']
    permission_classes = (SuperUserOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(methods=['patch', 'get'], detail=False,
            permission_classes=[SuperUserOrAdminOrModeratorOrAuthor,
                                permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(role=request.user.role)
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class CreateUserViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для создания обьектов класса User."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        """Создает объект класса User и
        отправляет на почту пользователя код подтверждения."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Ваш confirmation_code',
            message=(f'{user.username}, '
                     f'Ваш код подтверждения: {confirmation_code}, '
                     'отправьте его на адрес api/v1/auth/token, '
                     'для получения токена'),
            from_email='YamDB@yandex.ru',
            recipient_list=[request.data.get('email')],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """Вьюсет для получения токена."""
    queryset = User.objects.all()
    serializer_class = GetTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
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


class CategoryViewSet(CreateRetrieveDestroyViewSet):
    """Вьюсет для создания объектов Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов Title."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('category_slug', 'genre_slug', 'name', 'year')

    def get_serializer_class(self):
        """Определяет какой сериализатор использвать для Title."""
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов Review."""
    permission_classes = [SuperUserOrAdminOrModeratorOrAuthor]
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_title(self):
        """Получение объекта Title."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Получение queryset объекта Title."""
        title = self.get_title()
        return title.reviews

    def perform_create(self, serializer):
        """Переопределение поведения объекта Review при сохранении."""
        serializer.save(
            author=self.request.user,
            title=self.get_title(),
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов Comment."""
    permission_classes = [SuperUserOrAdminOrModeratorOrAuthor]
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_review(self):
        """Получение объекта Comment."""
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return get_object_or_404(
            Review, pk=self.kwargs.get('review_id'), title=title)

    def get_queryset(self):
        """Получение queryset объекта Comment."""
        review = self.get_review()
        return review.comments

    def perform_create(self, serializer):
        """Переопределение поведения объекта Comment при сохранении."""
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
