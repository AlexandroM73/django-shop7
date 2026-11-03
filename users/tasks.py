from datetime import timedelta
from celery import shared_task
from django.utils import timezone


@shared_task
def check_last_login():
    """Блокирует пользователей, не заходивших более 30 дней."""
    from users.models import User

    month_ago = timezone.now() - timedelta(days=30)

    # Находим активных пользователей, которые не заходили месяц
    users_to_block = User.objects.filter(
        is_active=True,
        last_login__lt=month_ago
    )

    count = users_to_block.update(is_active=False)
    print(f'[Celery] Заблокировано пользователей: {count}')
    return f'Blocked {count} users'
