from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.orders.models.cart import Cart
from apps.restaurants.models.coupon import Coupon, CouponUsage
from ..serializers.coupon import CouponListSerializer
from django.db.models.functions import Coalesce

from django.db.models import Q, Count, OuterRef, Subquery, IntegerField, F

class CouponViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        cart_ids = request.data.get("cart_id")

        if not cart_ids or not isinstance(cart_ids, list):
            return Response(
                {"detail": "cart_id is required and must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        carts = (
            Cart.objects.select_related("restaurant")
            .prefetch_related("items")
            .filter(
                id__in=cart_ids,
                user=request.user,
                status=Cart.Status.ACTIVE,
            )
        )

        if not carts.exists():
            return Response(
                {"detail": "No valid carts found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        now = timezone.now()

        restaurant_ids = carts.values_list("restaurant_id", flat=True)

        # 🔥 Subquery to count usage per user per coupon
        usage_subquery = (
            CouponUsage.objects.filter(
                user=request.user,
                coupon=OuterRef("pk"),
            )
            .values("coupon")
            .annotate(c=Count("id"))
            .values("c")[:1]
        )

        coupons = (
            Coupon.objects.filter(is_active=True)
            .filter(
                Q(valid_from__lte=now) | Q(valid_from__isnull=True),
                Q(valid_to__gte=now) | Q(valid_to__isnull=True),
            )
            .filter(
                Q(restaurant_specific__isnull=True)
                | Q(restaurant_specific__in=restaurant_ids)
            )
            .annotate(
                user_used_count=Coalesce(
                    Subquery(usage_subquery, output_field=IntegerField()),
                    0,
                )
            )
            # ✅ CRITICAL FILTER
            .filter(
                Q(usage_limit__isnull=True)
                | Q(user_used_count__lt=F("usage_limit"))
            )
            .distinct()
        )

        serializer = CouponListSerializer(coupons, many=True)

        return Response({"coupons": serializer.data})