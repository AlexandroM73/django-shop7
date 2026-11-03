import re
from django.core.exceptions import ValidationError

YOUTUBE_REGEX = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
)
RUTUBE_REGEX = re.compile(
    r'^(https?://)?(www\.)?rutube\.ru/play/embed/([a-zA-Z0-9-]{36})'
)


def validate_video_link(value):
    if not value:
        raise ValidationError("Ссылка на видео обязательна.")

    if YOUTUBE_REGEX.match(value) or RUTUBE_REGEX.match(value):
        return value

    raise ValidationError(
        "Некорректная ссылка. Поддерживаются только YouTube (watch?v= или youtu.be) и RuTube."
    )
