from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'duration'] # Или все поля: '__all__'

class CourseSerializer(serializers.ModelSerializer):
    num_lessons = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'num_lessons', 'lessons']

    def get_num_lessons(self, obj):
        # related_name='lessons' из модели Lesson
        return obj.lessons.count()
