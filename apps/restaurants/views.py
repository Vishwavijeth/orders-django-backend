from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from apps.restaurants.models import Restaurant, Menu
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsRestaurantAdmin, IsRestaurantOwnerOrReadOnly, IsMenuOwnerOrReadOnly
from .serializers.restaurants import RestaurantSerializer, MenuSerializer
from .serializers.coupon import CouponListSerializer
from .pagination import MenuPagination
from apps.orders.models import Cart
from .models import Coupon

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

class CouponViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        cart_ids = request.data.get("cart_id")
        if not cart_ids or not isinstance(cart_ids, list):
            return Response(
                {"detail": "cart_id is required and must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        carts = Cart.objects.select_related("restaurant").prefetch_related("items").filter(
            id__in=cart_ids, user=request.user, status=Cart.Status.ACTIVE
        )
        if not carts.exists():
            return Response({"detail": "No valid carts found."}, status=status.HTTP_404_NOT_FOUND)
        
        now = timezone.now()

        coupons = Coupon.objects.filter(
            is_active=True
        ).filter(
            Q(valid_from__lte=now) | Q(valid_from__isnull=True),
            Q(valid_to__gte=now) | Q(valid_to__isnull=True)
        ).filter(
            Q(restaurant_specific__isnull=True) |  # global coupons
            Q(restaurant_specific__in=[cart.restaurant for cart in carts])
        ).distinct()

        coupon_serializer = CouponListSerializer(coupons, many=True)

        return Response({
            "coupons": coupon_serializer.data
        })