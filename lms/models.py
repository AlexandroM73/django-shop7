from django.db import models

class Course(models.Model):
    title = models.CharField('название', max_length=255)
    preview = models.ImageField('превью', upload_to='course_previews/', blank=True, null=True)
    description = models.TextField('описание', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        related_name='lessons',
        on_delete=models.CASCADE,
        verbose_name='курс'
    )
    title = models.CharField('название', max_length=255)
    description = models.TextField('описание', blank=True)
    preview = models.ImageField('превью', upload_to='lesson_previews/', blank=True, null=True)
    video_link = models.URLField('ссылка на видео', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.course.title} — {self.title}"
