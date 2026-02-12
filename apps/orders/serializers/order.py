from rest_framework import serializers
from apps.orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="menu_item.name", read_only=True)
    price = serializers.DecimalField(
        source="menu_item.price",
        max_digits=8,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "menu_item",
            "name",
            "price",
            "quantity",
        )



class OrderSerializer(serializers.ModelSerializer):
    restaurant = serializers.CharField(source="restaurant.name", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "restaurant",
            "total_amount",
            "status",
            "items",
            "created_at"
        )