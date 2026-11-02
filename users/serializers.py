from rest_framework import serializers
from courses.models import Payment  # ✅ ПРАВИЛЬНО: берём из courses

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'  # Или перечисли конкретные поля, если нужно
