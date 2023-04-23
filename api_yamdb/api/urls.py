from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet, GenreViewSet, TitleViewSet,
    CreateUserViewSet, GetTokenViewSet, UserViewSet
)

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/auth/signup/',
         CreateUserViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('v1/auth/token/',
         GetTokenViewSet.as_view({'post': 'create'}),
         name='token'),
    path('v1/', include(router_v1.urls)),
]
