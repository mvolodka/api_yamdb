from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CreateUserViewSet, GetTokenViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/auth/signup/',
         CreateUserViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('v1/auth/token/',
         GetTokenViewSet.as_view({'post': 'create'}),
         name='token'),
    path('v1/', include(router.urls)),
]
