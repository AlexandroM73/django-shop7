from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счёт'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Используем СТРОКИ, чтобы избежать циклических импортов
    paid_course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_payments'
    )

    paid_lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lesson_payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-paid_at']

    def clean(self):
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError('Нужно указать либо курс, либо урок.')
        if self.paid_course and self.paid_lesson:
            raise ValidationError('Можно указать только курс ИЛИ только урок.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
