from rest_framework import serializers
from .models import Course, Lesson

# LessonSerializer (из Шага 1)
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'position']

# CourseSerializer (обновлённый)
class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'lessons_count', 'lessons']

    def get_lessons_count(self, obj):
        return obj.lessons.count()
