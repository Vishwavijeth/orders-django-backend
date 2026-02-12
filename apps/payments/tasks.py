from celery import shared_task
from django.db import transaction
from django.core.cache import cache
from apps.orders.models import Order, OrderItem, Cart
from apps.payments.models import Payment
from apps.users.utils import send_email
from apps.orders.cache_keys import cart_list_cache_key


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 5})
def create_orders_from_payment(self, payment_id):
    payment = Payment.objects.get(id=payment_id)

    with transaction.atomic():
        carts_qs = (
            payment.carts
            .select_for_update()
            .filter(status=Cart.Status.ACTIVE)
            .prefetch_related("items", "items__menu_item")
        )

        # affected_user_ids = set()

        for cart in carts_qs:
            total = sum(item.price_snapshot * item.quantity for item in cart.items.all())

            order = Order.objects.create(
                user=cart.user,
                restaurant=cart.restaurant,
                payment=payment,
                total_amount=total
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    menu_item=item.menu_item,
                    menu_name_snapshot=item.menu_name_snapshot,
                    price_snapshot=item.price_snapshot,
                    quantity=item.quantity
                )
                for item in cart.items.all()
            ])

            cart.status = Cart.Status.CHECKED_OUT
            cart.save(update_fields=["status"])

            #affected_user_ids.add(cart.user_id)
    
    send_order_confirmation_email(payment_id)

    # for user_id in affected_user_ids:
    #     cache.delete(cart_list_cache_key(user_id))


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 5})
def send_order_confirmation_email(self, payment_id):
    orders = (
        Order.objects
        .filter(payment_id=payment_id)
        .select_related("user")
        .prefetch_related("items__menu_item")
    )

    if not orders.exists():
        return

    user = orders.first().user

    items = []
    total_amount = 0

    for order in orders:
        total_amount += order.total_amount
        for item in order.items.all():
            items.append(
                f"- {item.menu_item.name} x {item.quantity} (₹{item.price})"
            )

    message = f"""
                    Hi {user.username},

                    🎉 Your order has been placed successfully!

                    Payment ID: {orders.first().razorpay_payment_id}
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