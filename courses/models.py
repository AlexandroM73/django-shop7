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


class Payment(models.Model):
    # Было: related_name='payments'
    # Стало: related_name='course_payments' (уникальное имя!)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_payments'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField(help_text="Цена в копейках/центах")
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} for {self.course.title} ({self.status})"
