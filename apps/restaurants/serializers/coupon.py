from rest_framework import serializers
from ..models.coupon import Coupon

class CouponListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
            "discount_type",
            "discount_value",
            "max_discount_amount",
            "min_order_amount",
            "valid_from",
            "valid_to",
        ]