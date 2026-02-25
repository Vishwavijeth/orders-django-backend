from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError

def validate_and_calculate_coupon(carts, coupon):

    now = timezone.now()

    # BASIC VALIDATIONS
    if not coupon.is_active:
        raise ValidationError("Coupon is inactive")

    if coupon.valid_from and coupon.valid_from > now:
        raise ValidationError("Coupon not yet valid")

    if coupon.valid_to and coupon.valid_to < now:
        raise ValidationError("Coupon expired")

    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        raise ValidationError("Coupon usage limit reached")

    # RESTAURANT ANALYSIS
    restaurant_ids = set(carts.values_list("restaurant_id", flat=True))
    multi_restaurant = len(restaurant_ids) > 1

    # RESTAURANT-SPECIFIC RULE
    if coupon.restaurant_specific:

        if multi_restaurant:
            raise ValidationError(
                "Restaurant specific coupon cannot be used for multiple restaurants"
            )

        if coupon.restaurant_id not in restaurant_ids:
            raise ValidationError(
                "Coupon not valid for selected restaurant"
            )

        eligible_carts = carts.filter(restaurant_id=coupon.restaurant_id)

    else:
        eligible_carts = carts

    # CALCULATE ELIGIBLE TOTAL
    eligible_total = Decimal("0.00")

    for cart in eligible_carts.prefetch_related("items"):
        for item in cart.items.all():
            eligible_total += item.price_snapshot * item.quantity

    # MIN ORDER CHECK
    if coupon.min_order_value and eligible_total < coupon.min_order_value:
        raise ValidationError(
            f"Minimum order value should be {coupon.min_order_value}"
        )

    # DISCOUNT CALCULATION
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