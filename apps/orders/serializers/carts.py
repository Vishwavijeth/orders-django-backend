from rest_framework import serializers
from apps.orders.models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="menu_item.name", read_only=True)
    price = serializers.DecimalField(
        source="menu_item.price",
        max_digits=8,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = ("id", "name", "price", "quantity")

class CartSerializer(serializers.ModelSerializer):    
    restaurant = serializers.CharField(source="restaurant.name", read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only = True
    )

    class Meta:
        model = Cart
        fields = ("id", "restaurant", "items", "subtotal")