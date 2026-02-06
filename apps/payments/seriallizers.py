from rest_framework import serializers
from apps.orders.models import Cart
from apps.orders.models import Order, OrderItem
from .models import Payment

class InitiatePaymentSerializer(serializers.ModelSerializer):
    cart_item_ids = serializers.ListField(
        child = serializers.ListField(),
        allow_empty=False
    )

class CreatePaymentSerializer(serializers.Serializer):
    cart_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )