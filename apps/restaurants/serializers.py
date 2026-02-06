from rest_framework import serializers
from .models import Restaurant, Menu

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'is_active']

class ListRestaurantSerializer(serializers.ModelSerializer):

    owner = serializers.CharField(source='owner.username', read_only=True)
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'owner']

class MenuCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'restaurant', 'name', 'price', 'is_available', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        restaurant = attrs.get('restaurant')

        # Role check
        if user.role != user.Role.RESTAURANT_ADMIN:
            raise serializers.ValidationError(
                {"detail": "Only restaurant admins can add menu items."}
            )

        if restaurant.owner_id != user.id:
            raise serializers.ValidationError(
                {"detail": "You do not own this restaurant."}
            )

        return attrs


class ListAllMenuSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(
        source = 'restaurant.name',
        read_only = True
    )

    class Meta:
        model = Menu
        fields = ['id', 'name', 'restaurant_name', 'price', 'is_available']