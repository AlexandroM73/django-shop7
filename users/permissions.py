from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешает доступ только владельцу объекта (user == request.user)."""

    def has_object_permission(self, request, view, obj):
        # Для операций чтения (GET, HEAD, OPTIONS) разрешаем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для записи (PUT, PATCH, DELETE) проверяем, что юзер — владелец
        return obj.user == request.user


class IsModerator(permissions.BasePermission):
    """Проверяет, состоит ли пользователь в группе 'Moderator'."""

    def has_permission(self, request, view):
        # Если пользователь не авторизован, сразу False
        if not request.user.is_authenticated:
            return False

        # Ищем группу с именем 'Moderator'
        return request.user.groups.filter(name='Moderator').exists()
