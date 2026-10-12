from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    Позволяет читать и создавать платежи через API.
    """

    class Meta:
        model = Payment
        fields = '__all__'  # Или явно перечисли поля, как в примере выше

        # Опционально: если нужно форматировать дату или деньги особым образом,
        # можно добавить методы validate_<field> или to_representation.
