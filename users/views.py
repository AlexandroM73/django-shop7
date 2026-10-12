from rest_framework import viewsets
# from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import PaymentSerializer
from rest_framework import viewsets
# from .filters import PaymentFilter

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# class PaymentViewSet(viewsets.ModelViewSet):
#     queryset = Payment.objects.all()
#     serializer_class = PaymentSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = PaymentFilter
#     ordering_fields = ['paid_at']
#     ordering = ['-paid_at']  # сортировка по умолчанию
