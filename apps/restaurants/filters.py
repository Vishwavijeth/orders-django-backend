from django_filters import rest_framework as filters
from apps.restaurants.models.restaurant import Menu, Restaurant

class MenuListFilter(filters.FilterSet):

    restaurant = filters.ModelChoiceFilter(
        field_name="restaurant",
        queryset=Restaurant.objects.all()
    )
    is_available = filters.BooleanFilter(field_name="is_available")

    class Meta:
        model = Menu
        fields = [
            "restaurant",
            "is_available",
        ]
