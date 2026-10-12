from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreateView, LessonDetailView
from users.views import PaymentViewSet

# Создаём роутер и регистрируем ViewSet-ы
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Все роуты из router (courses, payments)
    path('', include(router.urls)),

    # Эндпоинты для уроков (не через роутер)
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
]
