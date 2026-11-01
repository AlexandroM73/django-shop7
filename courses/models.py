from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='courses/', blank=True, null=True)
    description = models.TextField()

    # ДОБАВЛЕНО: Владелец курса
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    preview = models.ImageField(upload_to='lessons/', blank=True, null=True)
    video_link = models.URLField()

    # ДОБАВЛЕНО: Владелец урока (обычно тот же, кто создал курс, но храним явно)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name='lessons'
    )

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_subscription')
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.course.title}"
