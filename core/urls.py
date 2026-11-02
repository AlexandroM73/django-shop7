from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home

# 👇 ДОБАВЬ ЭТОТ ИМПОРТ (для Swagger/Redoc)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Твой API (сюда входит courses/urls.py)
    path('api/', include('lms.urls')),

    # 👇 ДОБАВЬ ЭТИ ДВЕ СТРОКИ СРАЗУ ПОСЛЕ api/
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Главная страница (ловит только чистый /, не трогает /api/...)
    path('', home),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
