from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# --- 1. МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ (Обязательно для AUTH_USER_MODEL) ---
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# --- 2. МОДЕЛЬ ПЛАТЕЖА (Твой существующий код) ---
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
