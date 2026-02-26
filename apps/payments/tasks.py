from celery import shared_task
from django.db import transaction
from decimal import Decimal
from django.db.models import F
from apps.orders.models.order import Order, OrderItem
from apps.orders.models.cart import Cart
from apps.payments.models import Payment
from apps.restaurants.models.coupon import CouponUsage, Coupon
from apps.users.utils import send_email
from .utils.coupon_helper import validate_and_calculate_coupon

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 5},
)
def create_orders_from_payment(self, payment_id):
    payment = Payment.objects.select_related("coupon", "user").get(id=payment_id)
    coupon = payment.coupon
    user = payment.user

    with transaction.atomic():
        carts_qs = (
            payment.carts.select_for_update()
            .filter(status=Cart.Status.ACTIVE)
            .prefetch_related("items", "items__menu_item", "restaurant")
        )

        orders_created = []

        for cart in carts_qs:
            total = sum(
                item.price_snapshot * item.quantity
                for item in cart.items.all()
            )

            discount_applied = Decimal("0.00")
            discounted_total = total
            applied_coupon = None

            # 🔥 REVALIDATE COUPON
            if coupon:
                try:
                    discount_applied = validate_and_calculate_coupon(
                        payment.carts.filter(id=cart.id),
                        coupon,
                        user,
                    )
                    discounted_total = total - discount_applied
                    applied_coupon = coupon
                except Exception:
                    discount_applied = Decimal("0.00")
                    discounted_total = total
                    applied_coupon = None

            order = Order.objects.create(
                user=cart.user,
                restaurant=cart.restaurant,
                cart=cart,
                payment=payment,
                total_amount=discounted_total,
                discounted_applied=discount_applied,
                coupon=applied_coupon,
            )

            orders_created.append(order)

            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        menu_item=item.menu_item,
                        menu_name_snapshot=item.menu_name_snapshot,
                        price_snapshot=item.price_snapshot,
                        quantity=item.quantity,
                    )
                    for item in cart.items.all()
                ]
            )

            cart.status = Cart.Status.CHECKED_OUT
            cart.save(update_fields=["status"])

        # 🔥 PER USER USAGE TRACKING (FIXED)
        if coupon and orders_created:
            CouponUsage.objects.get_or_create(
                user=user,
                coupon=coupon,
                order=orders_created[0],
            )

    send_order_confirmation_email.delay(payment_id)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 5})
def send_order_confirmation_email(self, payment_id):
    orders = (
        Order.objects
        .filter(payment_id=payment_id)
        .select_related("user", "payment", "coupon")
        .prefetch_related("items__menu_item")
    )

    if not orders.exists():
        return

    first_order = orders.first()
    user = first_order.user
    payment_obj = first_order.payment

    items = []
    original_total = 0
    total_discount = 0
    final_total = 0
    coupon_used = None

    for order in orders:
        # Reconstruct original total from items
        order_original_total = sum(
            item.price_snapshot * item.quantity
            for item in order.items.all()
        )

        original_total += order_original_total
        total_discount += order.discounted_applied or 0
        final_total += order.total_amount

        if order.coupon and not coupon_used:
            coupon_used = order.coupon

        for item in order.items.all():
            items.append(
                f"- {item.menu_name_snapshot} x {item.quantity} (₹{item.price_snapshot})"
            )

    # -------- Email Content -------- #

    if coupon_used:
        message = f"""
Hi {user.username},

🎉 Your order has been placed successfully!

Payment ID: {payment_obj.payment_id}

Items Ordered:
{chr(10).join(items)}

-----------------------------------
Original Amount : ₹{original_total}
Coupon Applied  : {coupon_used.code}
Discount        : -₹{total_discount}
-----------------------------------
Final Paid      : ₹{final_total}
-----------------------------------

Thank you for ordering with us!
"""
    else:
        message = f"""
Hi {user.username},

🎉 Your order has been placed successfully!

Payment ID: {payment_obj.payment_id}

Items Ordered:
{chr(10).join(items)}

-----------------------------------
Total Amount : ₹{original_total}
-----------------------------------

Thank you for ordering with us!
"""

    send_email(
        subject="Your order has been placed",
        message=message,
        recipient=user.email
    )
