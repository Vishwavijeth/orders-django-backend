from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from apps.restaurants.models import Restaurant, Menu
from .serializers import RestaurantSerializer, ListRestaurantSerializer, MenuCreateSerializer, ListAllMenuSerializer

class IsRestaurantOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
    
class RestaurantViewSet(viewsets.ModelViewSet):

    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated, IsRestaurantOwnerOrReadOnly]
    queryset = Restaurant.objects.all().select_related('owner').order_by('id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ListRestaurantsView(generics.ListAPIView):
    queryset = (
        Restaurant.objects
        .select_related("owner")
        .order_by("-created_at")
    )
    serializer_class = ListRestaurantSerializer
    permission_classes = [permissions.AllowAny]

class IsRestaurantAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'RESTAURANT_ADMIN'
        )

class MenuViewSet(ModelViewSet):
    serializer_class = MenuCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print('debug user : ', user.id, user.role, user.username)

        if user.role != user.Role.RESTAURANT_ADMIN:
            return Menu.objects.none()

        return (
            Menu.objects
            .select_related('restaurant')
            .filter(restaurant__owner=user)
            .order_by('id')
        )

    def perform_create(self, serializer):
        user = self.request.user
        
        print('request data : ', self.request.data)
        if user.role != user.Role.RESTAURANT_ADMIN:
            raise PermissionDenied("Only restaurant admins can add menu items.")

        restaurant_id = self.request.data.get('restaurant')

        try:
            restaurant = Restaurant.objects.get(
                id=restaurant_id,
                owner=user
            )
        except Restaurant.DoesNotExist:
            raise PermissionDenied("You do not own this restaurant.")

        serializer.save(restaurant=restaurant)

class MenuPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class ListAllAvailableMenuView(generics.ListAPIView):
    serializer_class = ListAllMenuSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Menu.objects.filter(is_available=True).select_related('restaurant').order_by('id','restaurant__name', 'name')
    pagination_class = MenuPagination