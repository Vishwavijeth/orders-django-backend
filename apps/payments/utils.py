from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce

from apps.orders.models import CartItem, Order

def _line_total_expression():
    """
    Reusable DB expression for price * quantity.
    Prevents mixed type errors.
    """
    return ExpressionWrapper(
        F("price_snapshot") * F("quantity"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )


def get_carts_total(cart_qs):
    """
    Total for multiple carts (single SQL).
    """
    return (
        CartItem.objects.filter(cart__in=cart_qs)
        .aggregate(
            total=Coalesce(
                Sum(_line_total_expression()),
                0,
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
    )


def annotate_cart_totals(cart_qs):
    """
    Annotate each cart with cart_total.
    """
    return cart_qs.annotate(
        cart_total=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("items__price_snapshot") * F("items__quantity"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            ),
            0,
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )


def get_payment_orders_total(payment_id):
    """
    Total across orders for a payment.
    """
    return (
        Order.objects.filter(payment_id=payment_id)
        .aggregate(
            total=Coalesce(
                Sum("total_amount"),
                0,
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
    )