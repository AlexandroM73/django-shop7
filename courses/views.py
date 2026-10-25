from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Course
from .serializers import CourseSerializer
from users.permissions import IsOwner, IsModerator


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    # permission_classes = [IsOwner]  <-- НЕ ставь это здесь глобально!

    def get_queryset(self):
        """
        Логика видимости:
        - Обычный юзер: видит только свои курсы.
        - Модератор: видит ВСЕ курсы.
        """
        user = self.request.user

        # Проверяем, является ли пользователь модератором
        is_moderator = user.groups.filter(name='Moderator').exists()

        if is_moderator:
            # Модератор видит всё
            return Course.objects.all()
        else:
            # Обычный юзер видит только то, что принадлежит ему
            return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        Запрещаем создание курсов МОДЕРАТОРАМ.
        Создавать может только обычный владелец.
        """
        user = self.request.user
        is_moderator = user.groups.filter(name='Moderator').exists()

        if is_moderator:
            return Response(
                {"detail": "Модераторы не могут создавать курсы."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Если всё ок, сохраняем с владельцем
        serializer.save(owner=user)

    def destroy(self, request, *args, **kwargs):
        """
        Запрещаем удаление МОДЕРАТОРАМ.
        Удалять может только владелец.
        """
        instance = self.get_object()
        user = request.user
        is_moderator = user.groups.filter(name='Moderator').exists()

        if is_moderator:
            return Response(
                {"detail": "Модераторы не могут удалять курсы."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Дополнительная проверка: если вдруг не модератор, то он должен быть владельцем
        if instance.owner != user:
            return Response(
                {"detail": "Вы можете удалять только свои курсы."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
