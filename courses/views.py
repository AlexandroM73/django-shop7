from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        is_moderator = user.groups.filter(name='Moderator').exists()

        if is_moderator:
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Moderator').exists():
            return Response(
                {"detail": "Модераторы не могут создавать курсы."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Проверка на модератора
        if request.user.groups.filter(name='Moderator').exists():
            return Response(
                {"detail": "Модераторы не могут удалять курсы."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверка, что это его курс
        if instance.owner != request.user:
            return Response(
                {"detail": "Вы можете удалять только свои курсы."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        is_moderator = user.groups.filter(name='Moderator').exists()

        if is_moderator:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        # Запрет для модераторов
        if request.user.groups.filter(name='Moderator').exists():
            return Response(
                {"detail": "Модераторы не могут создавать уроки."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SubscribeView(APIView):
    """
    Эндпоинт для подписки на курс.
    POST /api/courses/subscribe/
    Body: {"course": 1}
    """

    def post(self, request):
        course_id = request.data.get('course')

        if not course_id:
            return Response(
                {"detail": "Поле 'course' обязательно."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Курс с таким ID не найден."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {'course': course.id}
        serializer = SubscriptionSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception:
                # Ловим ошибку уникальности (пользователь уже подписан)
                return Response(
                    {"detail": "Вы уже подписаны на этот курс."},
                    status=status.HTTP_409_CONFLICT
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
