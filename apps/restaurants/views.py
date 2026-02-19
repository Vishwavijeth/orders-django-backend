from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from apps.restaurants.models import Restaurant, Menu
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsRestaurantAdmin, IsRestaurantOwnerOrReadOnly, IsMenuOwnerOrReadOnly
from .serializers import RestaurantSerializer, MenuSerializer
from .pagination import MenuPagination
    
class RestaurantViewSet(viewsets.ModelViewSet):

    # public can view, only owner can modify

    queryset = (
        Restaurant.objects.select_related("owner").order_by("-created_at")
    )
    serializer_class = RestaurantSerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly, IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

class MenuViewSet(ModelViewSet):
    """
    GET → public
    WRITE → restaurant admin only
    """

    serializer_class = MenuSerializer
    pagination_class = MenuPagination

    # dynamic permissions
    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [IsRestaurantAdmin(), IsMenuOwnerOrReadOnly()]

    # optimized queryset
    def get_queryset(self):
        user = self.request.user

        base_qs = (
            Menu.objects
            .select_related("restaurant", "restaurant__owner")
            .order_by("restaurant__name", "name")
        )

        # 🔹 public listing
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return base_qs.filter(is_available=True)

        # 🔹 admin view (only own restaurants)
        if user.is_authenticated and user.role == user.Role.RESTAURANT_ADMIN:
            return base_qs.filter(restaurant__owner=user)

        return Menu.objects.none()

    # safe create
    def perform_create(self, serializer):
        user = self.request.user
        restaurant_id = self.request.data.get("restaurant")

        restaurant = Restaurant.objects.filter(
            id=restaurant_id,
            owner=user,
        ).first()

        if not restaurant:
            raise PermissionDenied("You do not own this restaurant.")

        serializer.save(restaurant=restaurant)