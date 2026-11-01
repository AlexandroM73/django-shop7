from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_video_link

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'video_link', 'owner']
        read_only_fields = ['owner'] # Владелец не приходит с фронтенда

    def validate_video_link(self, value):
        return validate_video_link(value)

    def create(self, validated_data):
        # Автоматически подставляем текущего пользователя
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class CourseSerializer(serializers.ModelSerializer):
    num_lessons = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'num_lessons', 'lessons']

    def get_num_lessons(self, obj):
        return obj.lessons.count()

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Subscription.objects.create(**validated_data)
