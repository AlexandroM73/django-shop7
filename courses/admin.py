from django.contrib import admin
from .models import Course, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # Оставляем только то, что реально есть в модели (title, description и т.д.)
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
