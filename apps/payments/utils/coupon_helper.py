from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.restaurants.models.coupon import CouponUsage

def validate_and_calculate_coupon(carts, coupon, user):
    now = timezone.now()

    if not coupon.is_active:
        raise ValidationError("Coupon is inactive")

    if coupon.valid_from and coupon.valid_from > now:
        raise ValidationError("Coupon not yet valid")

    if coupon.valid_to and coupon.valid_to < now:
        raise ValidationError("Coupon expired")

    if coupon.usage_limit:
        user_usage_count = (
            CouponUsage.objects
            .filter(user=user, coupon=coupon)
            .count()
        )

        if user_usage_count >= coupon.usage_limit:
            raise ValidationError(
                "You have already used this coupon maximum allowed times"
            )

    restaurant_ids = set(carts.values_list("restaurant_id", flat=True))
    multi_restaurant = len(restaurant_ids) > 1

    coupon_restaurant_ids = set(
        coupon.restaurant_specific.values_list("id", flat=True)
    )

    if coupon_restaurant_ids:

        if multi_restaurant:
            raise ValidationError(
                "Restaurant specific coupon cannot be used for multiple restaurants"
            )

        if not restaurant_ids.intersection(coupon_restaurant_ids):
            raise ValidationError("Coupon not valid for selected restaurant")

        eligible_carts = carts.filter(
            restaurant_id__in=coupon_restaurant_ids
        )
    else:
        eligible_carts = carts

    eligible_total = Decimal("0.00")

    for cart in eligible_carts.prefetch_related("items"):
        for item in cart.items.all():
            eligible_total += item.price_snapshot * item.quantity

    if coupon.min_order_amount and eligible_total < coupon.min_order_amount:
        raise ValidationError(
            f"Minimum order value should be {coupon.min_order_amount}"
        )

    if coupon.discount_type == coupon.DiscountType.FLAT:
        discount = min(coupon.discount_value, eligible_total)

    elif coupon.discount_type == coupon.DiscountType.PERCENTAGE:
        discount = (
            eligible_total * coupon.discount_value / Decimal("100.00")
        ).quantize(Decimal("0.01"))

        if coupon.max_discount_amount:
            discount = min(discount, coupon.max_discount_amount)
    else:
        discount = Decimal("0.00")

    return discount