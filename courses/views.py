from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer

# --- НОВЫЕ ИМПОРТЫ ДЛЯ STRIPE И ДОКУМЕНТАЦИИ ---
from .stripe_service import create_stripe_product_and_price, create_checkout_session
from drf_spectacular.utils import extend_schema


# -----------------------------------------------


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


# --- НОВЫЙ КЛАСС ДЛЯ ОПЛАТЫ (STRIPE) ---
@extend_schema(
    description="Запускает процесс оплаты курса через Stripe. Создает продукт, цену и сессию оплаты.",
    request=None,
    responses={
        200: {
            "type": "object",
            "properties": {
                "payment_id": {"type": "integer", "description": "ID платежа в нашей БД"},
                "stripe_session_id": {"type": "string", "description": "ID сессии Stripe"},
                "url": {"type": "string", "description": "Ссылка на страницу оплаты"}
            }
        },
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
        404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        500: {"type": "object", "properties": {"error": {"type": "string"}}}
    }
)
class PurchaseCourseView(APIView):
    """
    Запускает процесс оплаты курса.
    На вход: id курса.
    На выход: ссылка на оплату Stripe и ID платежа в нашей БД.
    """

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, id=course_id)
        user = request.user

        # ЦЕНА В ЦЕНТАХ (для USD) или КОПЕЙКАХ (для RUB).
        # В реальном проекте лучше брать из course.price, здесь фиксировано для теста.
        amount_cents = 1000

        try:
            # 1. Создаем продукт и цену в Stripe
            price_id = create_stripe_product_and_price(course, amount_cents)

            # 2. Формируем URL для успеха и отмены
            # ВАЖНО: Эти URL должны существовать в твоем фронтенде.
            # Для теста можно оставить заглушками, но Stripe требует валидные URL.
            success_url = "http://127.0.0.1:8000/payment-success"
            cancel_url = "http://127.0.0.1:8000/payment-cancel"

            # 3. Создаем сессию и получаем ссылку
            session_id, url, payment_id = create_checkout_session(
                user=user,
                course=course,
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                amount_cents=amount_cents
            )

            return Response({
                "payment_id": payment_id,
                "stripe_session_id": session_id,
                "url": url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # В продакшене тут нужен logger.error()
            print(f"Stripe Error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# -------------------------------------------
