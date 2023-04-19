from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CommentsViewSet, ReviewsViewSet,
    CategoriesViewSet, GenresViewSet, TitleViewSet
)
from api.views import UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('categories', CategoriesViewSet, basename='categories')
router.register('genres', GenresViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(
    r'^titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)
router.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/users/me/', UserViewSet.as_view(), name='me'),
    path('v1/auth/signup/', UserViewSet.as_view(), name='signup'),
    path('v1/auth/token/', UserViewSet.as_view(), name='token'),
    path('v1/', include(router.urls)),
]
