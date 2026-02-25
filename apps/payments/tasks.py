from celery import shared_task
from django.db import transaction
from decimal import Decimal
from django.db.models import F
from apps.orders.models.order import Order, OrderItem
from apps.orders.models.cart import Cart
from apps.payments.models import Payment
from apps.users.utils import send_email
from .utils.coupon_helper import validate_and_calculate_coupon

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 5})
def create_orders_from_payment(self, payment_id):
    payment = Payment.objects.get(id=payment_id)
    coupon = payment.coupon

    with transaction.atomic():
        carts_qs = (
            payment.carts.select_for_update()
            .filter(status=Cart.Status.ACTIVE)
            .prefetch_related("items", "items__menu_item", "restaurant")
        )

        for cart in carts_qs:
            total = sum(
                item.price_snapshot * item.quantity
                for item in cart.items.all()
            )

            discount_applied = Decimal("0.00")
            discounted_total = total
            applied_coupon = None

            if coupon:
                try:
                    discount_applied = validate_and_calculate_coupon(
                        payment.carts.filter(id=cart.id),
                        coupon,
                    )
                    discounted_total = total - discount_applied
                    applied_coupon = coupon
                except Exception:
                    # safety fallback
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

        if coupon:
            coupon.refresh_from_db()

            if not coupon.usage_limit:
                coupon.used_count = F("used_count") + 1
                coupon.save(update_fields=["used_count"])
            else:
                coupon.used_count = F("used_count") + 1
                coupon.save(update_fields=["used_count"])

                coupon.refresh_from_db()

                if coupon.used_count >= coupon.usage_limit and coupon.is_active:
                    coupon.is_active = False
                    coupon.save(update_fields=["is_active"])

    send_order_confirmation_email.delay(payment_id)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 5})
def send_order_confirmation_email(self, payment_id):
    orders = (
        Order.objects
        .filter(payment_id=payment_id)
        .select_related("user", "payment")
        .prefetch_related("items__menu_item")
    )

    if not orders.exists():
        return

    first_order = orders.first()
    user = first_order.user
    payment_obj = first_order.payment

    items = []
    total_amount = 0

    for order in orders:
        total_amount += order.total_amount
        for item in order.items.all():
            items.append(
                f"- {item.menu_item.name} x {item.quantity} (₹{item.price_snapshot})"
            )

    message = f"""
Hi {user.username},

🎉 Your order has been placed successfully!

Payment ID: {payment_obj.payment_id}
Total Amount: ₹{total_amount}

Items Ordered:
{chr(10).join(items)}

Thank you for ordering with us!
"""

    send_email(
        subject="Your order has been placed",
        message=message,
        recipient=user.email
    )
