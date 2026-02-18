from rest_framework import serializers

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