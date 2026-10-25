from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока (используется как вложенный в курсе)"""

    class Meta:
        model = Lesson
        # Лучше не использовать '__all__' в вложенных сериализаторах — так API будет чище.
        # Оставь только самое важное. Если нужны все поля — поставь '__all__'.
        fields = ['id', 'title', 'duration']  # добавь сюда свои ключевые поля


class CourseSerializer(serializers.ModelSerializer):
    # ЗАДАНИЕ 1: поле количества уроков через SerializerMethodField
    num_lessons = serializers.SerializerMethodField()

    # ЗАДАНИЕ 3: вложенный сериализатор для списка уроков
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        # Важно: явно перечисли поля, чтобы num_lessons и lessons попали в ответ
        fields = ['id', 'title', 'description', 'num_lessons', 'lessons']

    def get_num_lessons(self, obj):
        """
        Возвращает количество уроков в курсе.

        ⚠️ ВАЖНО: Имя 'lessons' должно совпадать с related_name в твоей модели Lesson
        или с именем поля ManyToMany в модели Course.

        Если в модели Lesson есть: course = models.ForeignKey(Course, ...),
        то связь будет obj.lesson_set.count().

        Если у тебя в Course есть: lessons = models.ManyToManyField(Lesson),
        то оставляем obj.lessons.count().
        """
        # Попробуй этот вариант сначала:
        return obj.lessons.count()

        # Если получишь ошибку AttributeError, раскомментируй строку ниже и закомментируй верхнюю:
        # return obj.lesson_set.count()
