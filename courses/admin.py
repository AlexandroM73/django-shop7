from django.contrib import admin
from .models import Course, Lesson, Payment  # <-- ДОБАВЬ Payment сюда!

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)

# <-- ДОБАВЬ ЭТОТ БЛОК В САМЫЙ КОНЕЦ ФАЙЛА
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Удобно сразу видеть: кто, за что, какой статус, когда
    list_display = ('id', 'user', 'course', 'status', 'amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'course__title', 'stripe_session_id')
    readonly_fields = ('stripe_session_id', 'stripe_payment_intent_id')
