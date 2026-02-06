from rest_framework import serializers, mixins, viewsets
from apps.orders.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='menu_items.name', read_only=True)
    price = serializers.DecimalField(
        source='menu_items.price',
        max_digits=8,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = ('id', 'name', 'price', 'quantity')

class CartSerializer(serializers.ModelSerializer):
    restaurant = serializers.CharField(source='restaurant.name', read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'restaurant', 'items', 'subtotal')

    def get_subtotal(self, obj):
        return sum(
            item.menu_items.price * item.quantity
            for item in obj.items.all()
        )
    
#list cart
class CartItemListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='menu_items.name', read_only=True)
    price = serializers.DecimalField(
        source='menu_items.price',
        max_digits=8,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = ('id', 'name', 'price', 'quantity')

class CartListSerializer(serializers.ModelSerializer):
    restaurant = serializers.CharField(source='restaurant.name', read_only=True)
    items = CartItemListSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'restaurant', 'items', 'subtotal')

    def get_subtotal(self, obj):
        return sum(item.menu_items.price * item.quantity for item in obj.items.all())