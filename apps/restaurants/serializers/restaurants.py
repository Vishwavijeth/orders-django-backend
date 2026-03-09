from rest_framework import serializers
from apps.common.serializers import AppReadOnlyModelSerializer
from ..models.restaurant import Restaurant, Menu

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


class MenuListModelSerializer(AppReadOnlyModelSerializer):
    restaurant_name = serializers.CharField(
        source="restaurant.name",
        read_only=True,
    )

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Menu
        fields = [
            "id",
            "restaurant_name",
            "name",
            "price",
            "is_available",
        ]
    
    def get_filter_meta(self):
        
        restaurants = Restaurant.objects.all()

        return {
            "is_available": self.serialize_dj_choices(
                [
                    (True, "Available"),
                    (False, "Not Available"),
                ]
            ),
            "restaurant": [
                {"id": r.id, "identity": r.name}
                for r in restaurants
            ],
        }