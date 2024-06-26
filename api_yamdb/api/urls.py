from api.views import (CategoryViewSet, CommentViewSet,
                       CreateOrSignupUserViewSet, GenreViewSet,
                       GetTokenViewSet, ReviewViewSet, TitleViewSet,
                       UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
    basename='review')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/',
         CreateOrSignupUserViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('v1/auth/token/',
         GetTokenViewSet.as_view({'post': 'create'}),
         name='token')
]
