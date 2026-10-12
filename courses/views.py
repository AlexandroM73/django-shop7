from rest_framework import viewsets
from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    API для курсов: список, детали, создание, обновление, удаление.

    prefetch_related('lessons') здесь критически важен:
    - без него будет N+1 запросов (по одному SELECT для каждого курса, чтобы получить уроки),
    - с ним все уроки загружаются одним дополнительным запросом, а count() считается в Python.
    Это особенно важно при работе с PostgreSQL и большими списками.
    """
    queryset = Course.objects.prefetch_related('lessons').all()
    serializer_class = CourseSerializer

