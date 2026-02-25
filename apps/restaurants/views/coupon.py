from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.orders.models.cart import Cart
from apps.restaurants.models.coupon import Coupon
from ..serializers.coupon import CouponListSerializer
from django.db.models import Q

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