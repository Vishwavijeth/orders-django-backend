from rest_framework import serializers
from .models import Restaurant, Menu

class RestaurantSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'is_active', 'owner']

class MenuSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(
        source="restaurant.name",
        read_only=True,
    )

    class Meta:
        model = Menu
        fields = [
            "id",
            "restaurant",
            "restaurant_name",
            "name",
            "price",
            "is_available",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]