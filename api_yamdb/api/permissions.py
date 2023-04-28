from rest_framework import permissions


class AnonimReadOnly(permissions.BasePermission):
    """Разрешает анонимному пользователю только безопасные запросы."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class SuperUserOrAdmin(permissions.BasePermission):
    """
    Предоставляет права на осуществление запросов
    только суперпользователю Джанго, админу Джанго или
    аутентифицированному пользователю с ролью admin.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_admin)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_admin)
        )


class Moderator(permissions.BasePermission):
    """
    Предоставляет права на осуществление запросов
    пользователю с ролью модертор
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_moderator
        )


class Author(permissions.BasePermission):
    """
    Предоставляет права на осуществление запросов
    автору объекта
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and request.user == obj.author
        )
