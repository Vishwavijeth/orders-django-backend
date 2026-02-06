from celery import shared_task
from django.db import transaction
from apps.orders.models import Order, OrderItem, CartItem
from apps.payments.models import Payment
from apps.users.utils import send_email

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 5})
def create_orders_from_payment(self, payment_id):
    payment = Payment.objects.select_related().prefetch_related(
        "carts__items__menu_items"
    ).get(id=payment_id)

    with transaction.atomic():
        for cart in payment.carts.all():
            order = Order.objects.create(
                user=cart.user,
                payment=payment,
                status=Order.Status.PAID,
                total_amount=sum(
                    item.menu_items.price * item.quantity
                    for item in cart.items.all()
                ),
                razorpay_payment_id=payment.razorpay_payment_id
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    menu_item=item.menu_items,
                    restaurant=item.menu_items.restaurant,
                    price=item.menu_items.price,
                    quantity=item.quantity
                )
                for item in cart.items.all()
            ])

            cart.delete()

        payment.carts.clear()

    # Send mail AFTER everything is saved
    send_order_confirmation_email.delay(payment.id)


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