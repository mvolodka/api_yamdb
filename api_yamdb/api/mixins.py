from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from api.permissions import AnonimReadOnly, SuperUserOrAdmin


class CreateRetrieveDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (AnonimReadOnly | SuperUserOrAdmin,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
